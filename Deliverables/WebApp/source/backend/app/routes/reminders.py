"""
Tutunaku - Rutas de Recordatorios
Configuración de alarmas diarias para estudiar
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundError
from app.models.mysql_models import Reminder
from app.schemas.schemas import ReminderCreate, ReminderUpdate, ReminderResponse, StandardResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get("", response_model=list[ReminderResponse])
async def get_my_reminders(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene los recordatorios del usuario."""
    result = await db.execute(
        select(Reminder).where(Reminder.user_id == user_id)
    )
    return result.scalars().all()


@router.post("", response_model=StandardResponse, status_code=201)
async def create_reminder(
    data: ReminderCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Crea un recordatorio de estudio."""
    # Máximo 3 recordatorios por usuario
    count_result = await db.execute(
        select(Reminder).where(Reminder.user_id == user_id)
    )
    existing = count_result.scalars().all()
    if len(existing) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 3 recordatorios permitidos por usuario"
        )

    reminder = Reminder(
        user_id=user_id,
        hour=data.hour,
        minute=data.minute,
        timezone=data.timezone,
        message=data.message or "¡Es hora de estudiar totonaco!",
        days_of_week=data.days_of_week,
        is_active=True,
    )
    db.add(reminder)
    await db.commit()

    logger.info("reminder_created", user_id=user_id, hour=data.hour, minute=data.minute)
    return StandardResponse(
        message="Recordatorio creado",
        data={"id": reminder.id, "time": f"{data.hour:02d}:{data.minute:02d}"}
    )


@router.patch("/{reminder_id}", response_model=StandardResponse)
async def update_reminder(
    reminder_id: str,
    data: ReminderUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un recordatorio."""
    result = await db.execute(
        select(Reminder).where(
            and_(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundError("Recordatorio")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(reminder, key, value)

    await db.commit()
    return StandardResponse(message="Recordatorio actualizado")


@router.delete("/{reminder_id}", response_model=StandardResponse)
async def delete_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Elimina un recordatorio."""
    result = await db.execute(
        select(Reminder).where(
            and_(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundError("Recordatorio")

    await db.delete(reminder)
    await db.commit()
    return StandardResponse(message="Recordatorio eliminado")


# ============================================
# SERVICIO DE SCHEDULER (APScheduler)
# ============================================
async def process_due_reminders(db: AsyncSession):
    """
    Procesa recordatorios que deben enviarse ahora.
    Llamar desde el scheduler cada minuto.
    """
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_minute = now.minute
    current_weekday = now.weekday()  # 0=lunes, 6=domingo

    result = await db.execute(
        select(Reminder).where(
            and_(
                Reminder.is_active == True,
                Reminder.hour == current_hour,
                Reminder.minute == current_minute,
            )
        )
    )
    due_reminders = result.scalars().all()

    from app.routes.exercises import create_notification

    sent = 0
    for reminder in due_reminders:
        # Verificar día de la semana
        if current_weekday not in (reminder.days_of_week or list(range(7))):
            continue

        # Crear notificación en sistema (empuja en vivo a web + wearable)
        await create_notification(
            db, reminder.user_id,
            "reminder",
            "Recordatorio de estudio",
            reminder.message,
            "clock",
            action_url="/learn",
        )
        reminder.last_sent_at = now
        sent += 1

    if sent:
        await db.commit()
        logger.info("reminders_processed", count=sent)
