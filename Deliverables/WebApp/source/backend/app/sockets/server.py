"""
Tutunaku - Servidor Socket.IO (Dashboard en tiempo real, Etapa 14).

Socket.IO transmite información en tiempo real (predicciones, alertas,
métricas), pero esto NO implica que los modelos aprendan en tiempo real:
siguen siendo los mismos artefactos entrenados en los notebooks.

`sio` se combina con la app FastAPI en `app/main.py` mediante
`socketio.ASGIApp(sio, other_asgi_app=app)`, expuesto como una variable NUEVA
(`socket_app`) para no alterar `app` (usado tal cual por los tests existentes).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func, select
import socketio

from app.core.config import settings
from app.core.database import get_session_factory
from app.core.exceptions import MLInferenceError, MLModelUnavailableError
from app.core.security import decode_token
from app.models.mysql_models import ExerciseAttempt

logger = structlog.get_logger()

ADMIN_ROOM = "admin"


def user_room(user_id: str) -> str:
    """Sala personal de un usuario: la web y el wearable se unen ambos aquí."""
    return f"user:{user_id}"

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        settings.FRONTEND_URL,
    ],
)

_scheduler: AsyncIOScheduler | None = None


@sio.event
async def connect(sid, environ, auth):
    logger.info("socketio_client_connected", sid=sid)
    token = (auth or {}).get("token")
    if not token:
        return
    try:
        payload = decode_token(token)
    except Exception:  # noqa: BLE001 - un token inválido no debe rechazar la conexión
        return

    user_id = payload.get("sub")
    if user_id:
        # Sala personal: la app web y el wearable reciben ambos sus propios
        # eventos (user_stats_updated, new_notification) sin importar cuál
        # cliente los originó.
        await sio.enter_room(sid, user_room(user_id))

    if payload.get("role") == "admin":
        await sio.enter_room(sid, ADMIN_ROOM)
        logger.info("socketio_admin_joined_room", sid=sid)


@sio.event
async def disconnect(sid):
    logger.info("socketio_client_disconnected", sid=sid)


# ============================================
# Emisores (llamados desde app/routes/ml.py y los jobs periódicos)
# ============================================
async def emit_new_prediction(payload: dict) -> None:
    await sio.emit("new_prediction", payload)


async def emit_anomaly_alert(payload: dict) -> None:
    await sio.emit("anomaly_alert", payload)


async def emit_platform_load_update(payload: dict) -> None:
    await sio.emit("platform_load_update", payload)


async def emit_user_progress_update(payload: dict) -> None:
    await sio.emit("user_progress_update", payload)


# ── Actividad en vivo para el panel de administración (sala "admin") ──
async def emit_admin_new_user(payload: dict) -> None:
    await sio.emit("admin_new_user", payload, room=ADMIN_ROOM)


async def emit_admin_lesson_completed(payload: dict) -> None:
    await sio.emit("admin_lesson_completed", payload, room=ADMIN_ROOM)


async def emit_admin_xp_record(payload: dict) -> None:
    await sio.emit("admin_xp_record", payload, room=ADMIN_ROOM)


# ── Eventos personales (sala "user:<id>"): consumidos por la web Y el wearable ──
async def emit_user_stats_updated(user_id: str, payload: dict) -> None:
    await sio.emit("user_stats_updated", payload, room=user_room(user_id))


async def emit_new_notification(user_id: str, payload: dict) -> None:
    await sio.emit("new_notification", payload, room=user_room(user_id))


# ============================================
# Jobs periódicos (APScheduler) — también invocables manualmente
# (ver POST /api/ml/trigger/*) para poder demostrar los eventos al instante.
# ============================================
async def run_platform_load_update_job() -> None:
    from app.ml import service  # import diferido: evita ciclos al cargar el paquete

    try:
        forecast = await service.forecast_platform_load(horizon_hours=1)
        forecast["inference_date"] = forecast["inference_date"].isoformat()
        await emit_platform_load_update(forecast)
    except (MLModelUnavailableError, MLInferenceError) as exc:
        logger.warning("platform_load_update_skipped", error=str(exc))
    except Exception as exc:  # noqa: BLE001 - un job en background nunca debe tumbar el proceso
        logger.error("platform_load_update_failed", error=str(exc))


async def run_user_progress_update_job() -> None:
    """Agrega actividad reciente REAL de la app (solo lectura, sin modificarla)."""
    if settings.DB_TYPE not in ("mysql", "both"):
        return
    try:
        session_factory = get_session_factory()
        since = datetime.now(timezone.utc) - timedelta(minutes=15)
        async with session_factory() as session:
            result = await session.execute(
                select(
                    func.count(ExerciseAttempt.id),
                    func.coalesce(func.sum(ExerciseAttempt.xp_earned), 0),
                    func.count(func.distinct(ExerciseAttempt.user_id)),
                ).where(ExerciseAttempt.created_at >= since)
            )
            attempts_count, xp_sum, active_users = result.one()
        await emit_user_progress_update({
            "window_minutes": 15,
            "attempts_count": int(attempts_count or 0),
            "xp_gained": int(xp_sum or 0),
            "active_users": int(active_users or 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as exc:  # noqa: BLE001
        logger.warning("user_progress_update_skipped", error=str(exc))


async def run_process_due_reminders_job() -> None:
    """Dispara los recordatorios de estudio programados por los usuarios.

    Antes este trabajo (`process_due_reminders`) existía pero nunca se
    registraba en ningún scheduler, así que los recordatorios se guardaban
    pero jamás se enviaban. Se ejecuta cada minuto, alineado con la
    granularidad de hora/minuto de los recordatorios.
    """
    if settings.DB_TYPE not in ("mysql", "both"):
        return
    from app.routes.reminders import process_due_reminders  # import diferido: evita ciclos

    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await process_due_reminders(session)
    except Exception as exc:  # noqa: BLE001
        logger.error("reminders_job_failed", error=str(exc))


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_platform_load_update_job, "interval",
        seconds=settings.ML_PLATFORM_LOAD_INTERVAL_SECONDS, id="ml_platform_load_update",
    )
    _scheduler.add_job(
        run_user_progress_update_job, "interval",
        seconds=settings.ML_USER_PROGRESS_INTERVAL_SECONDS, id="ml_user_progress_update",
    )
    _scheduler.add_job(run_process_due_reminders_job, "interval", seconds=60, id="process_due_reminders")
    _scheduler.start()
    logger.info(
        "ml_socket_scheduler_started",
        platform_load_interval_s=settings.ML_PLATFORM_LOAD_INTERVAL_SECONDS,
        user_progress_interval_s=settings.ML_USER_PROGRESS_INTERVAL_SECONDS,
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("ml_socket_scheduler_stopped")
