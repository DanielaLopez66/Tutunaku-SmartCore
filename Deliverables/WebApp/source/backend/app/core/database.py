"""
Tutunaku - Configuración y conexión a base de datos
Soporta MySQL (SQLAlchemy) y MongoDB (Motor/Beanie)
"""
from motor.motor_asyncio import AsyncIOMotorClient
import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.base import Base
from app.core.config import settings

logger = structlog.get_logger()


# ============================================
# MySQL / SQLAlchemy
# ============================================
_mysql_engine = None
_AsyncSessionLocal = None


def get_mysql_engine():
    global _mysql_engine
    if _mysql_engine is None:
        # Convertir pymysql a aiomysql para async
        url = settings.MYSQL_DATABASE_URL.replace("pymysql", "aiomysql")
        _mysql_engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _mysql_engine


def get_session_factory():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_mysql_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_db():
    """Dependency para inyectar sesión de DB en rutas FastAPI."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================
# MongoDB / Motor
# ============================================
_mongo_client = None
_mongo_db = None


def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _mongo_client


def get_mongo_db():
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.MONGODB_DATABASE]
    return _mongo_db


# ============================================
# INICIALIZACIÓN
# ============================================
async def _init_mysql():
    """Inicializa la conexión a MySQL."""
    try:
        engine = get_mysql_engine()
        # Crear tablas si no existen (desarrollo)
        if settings.DEBUG:
            async with engine.begin() as conn:
                from app.models import mysql_models  # noqa - importa todos los modelos
                await conn.run_sync(Base.metadata.create_all)
        logger.info("mysql_connected", database=settings.MYSQL_DATABASE)
    except Exception as e:
        logger.error("mysql_connection_failed", error=str(e))
        raise


async def _init_mongodb():
    """Inicializa la conexión a MongoDB (Atlas o local)."""
    try:
        db = get_mongo_db()
        # Verificar conexión
        await db.command("ping")
        logger.info("mongodb_connected", database=settings.MONGODB_DATABASE, url=settings.MONGODB_URL[:40] + "...")
    except Exception as e:
        logger.error("mongodb_connection_failed", error=str(e))
        raise


async def init_db():
    """Inicializa la(s) base(s) de datos según configuración."""
    if settings.DB_TYPE == "both":
        # Conectar a ambas bases de datos simultáneamente
        await _init_mysql()
        await _init_mongodb()
        logger.info("both_databases_connected", mysql=settings.MYSQL_DATABASE, mongodb=settings.MONGODB_DATABASE)
    elif settings.DB_TYPE == "mysql":
        await _init_mysql()
    elif settings.DB_TYPE == "mongodb":
        await _init_mongodb()


async def close_db():
    """Cierra las conexiones a las bases de datos."""
    global _mysql_engine, _mongo_client, _mongo_db, _AsyncSessionLocal

    if _mysql_engine is not None:
        await _mysql_engine.dispose()
        _mysql_engine = None
        _AsyncSessionLocal = None
        logger.info("mysql_disconnected")

    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        logger.info("mongodb_disconnected")
