"""
Tutunaku API - Main Application Entry Point
Plataforma educativa gamificada para la lengua totonaca
"""
import asyncio
import sys
from typing import Dict

import socketio
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import close_db, get_mongo_db, get_mysql_engine, init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.sockets.server import sio, start_scheduler, stop_scheduler
from app.routes import (
    achievements,
    admin,
    auth,
    courses,
    exercises,
    lessons,
    ml,
    notifications,
    reminders,
    units,
    users,
)

if sys.platform == 'win32':
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    pass

# Configurar logging estructurado
configure_logging()
logger = structlog.get_logger()


def create_application() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    
    Configura middlewares, manejadores de excepciones, rutas, y eventos
    de ciclo de vida para la API de Tutunaku.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        ## Tutunaku API

        API REST para la plataforma educativa gamificada de lengua totonaca.

        ### Características:
        - Autenticación JWT con refresh tokens
        - Sistema de gamificación completo
        - Gestión de cursos y lecciones
        - Métricas y estadísticas
        - Sistema de notificaciones y recordatorios
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # === MIDDLEWARES ===

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            settings.FRONTEND_URL,
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Hosts confiables (producción)
    if not settings.DEBUG:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # === MANEJO DE EXCEPCIONES ===
    register_exception_handlers(application)

    # === RUTAS ===
    api_prefix = "/api/v1"

    application.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Autenticación"])
    application.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Usuarios"])
    application.include_router(courses.router, prefix=f"{api_prefix}/courses", tags=["Cursos"])
    application.include_router(units.router, prefix=f"{api_prefix}/units", tags=["Unidades"])
    application.include_router(lessons.router, prefix=f"{api_prefix}/lessons", tags=["Lecciones"])
    application.include_router(exercises.router, prefix=f"{api_prefix}/exercises", tags=["Ejercicios"])
    application.include_router(achievements.router, prefix=f"{api_prefix}/achievements", tags=["Logros"])
    application.include_router(notifications.router, prefix=f"{api_prefix}/notifications", tags=["Notificaciones"])
    application.include_router(reminders.router, prefix=f"{api_prefix}/reminders", tags=["Recordatorios"])
    application.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["Administración"])

    # API Inteligente (Machine Learning) - fuera de /api/v1 a propósito,
    # tal como especifica la guía del proyecto integrador.
    application.include_router(ml.router, prefix="/api/ml", tags=["Machine Learning"])

    # Archivos estáticos
    application.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # === EVENTOS DE CICLO DE VIDA ===
    @application.on_event("startup")
    async def startup_event():
        """Acciones a ejecutar al iniciar la aplicación."""
        logger.info("tutunaku_api_started", version=settings.APP_VERSION)
        await init_db()
        if settings.ENABLE_SCHEDULER:
            start_scheduler()

    @application.on_event("shutdown")
    async def shutdown_event():
        """Acciones a ejecutar al detener la aplicación."""
        logger.info("tutunaku_api_stopped")
        stop_scheduler()
        await close_db()

    # === HEALTH CHECK ===
    @application.get("/health", tags=["Sistema"])
    async def health_check() -> Dict:
        """
        Verifica el estado de salud de la aplicación y sus conexiones.
        """
        db_status = {"db_type": settings.DB_TYPE}

        # Check MySQL
        if settings.DB_TYPE in ("mysql", "both"):
            try:
                engine = get_mysql_engine()
                async with engine.connect() as conn:
                    from sqlalchemy import text
                    await conn.execute(text("SELECT 1"))
                db_status["mysql"] = "connected"
            except Exception as e:
                db_status["mysql"] = f"error: {str(e)[:80]}"

        # Check MongoDB
        if settings.DB_TYPE in ("mongodb", "both"):
            try:
                mongo_db = get_mongo_db()
                await mongo_db.command("ping")
                db_status["mongodb"] = "connected"
            except Exception as e:
                db_status["mongodb"] = f"error: {str(e)[:80]}"

        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "databases": db_status,
        }

    return application


app = create_application()

# ASGI app combinado con Socket.IO para servir el dashboard en tiempo real
# (Etapa 14). `app` se deja intacto para no romper los tests existentes que
# hacen `from app.main import app` con ASGITransport de httpx.
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
