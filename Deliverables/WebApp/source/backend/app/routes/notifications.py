"""Tutunaku - Rutas de Notificaciones"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.mysql_models import Notification
from app.schemas.schemas import NotificationResponse, StandardResponse

router = APIRouter()

@router.get("", response_model=list[NotificationResponse])
async def get_my_notifications(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()

@router.patch("/{notif_id}/read", response_model=StandardResponse)
async def mark_read(
    notif_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(
            and_(Notification.id == notif_id, Notification.user_id == user_id)
        )
    )
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.commit()
    return StandardResponse(message="Notificación marcada como leída")

@router.patch("/read-all", response_model=StandardResponse)
async def mark_all_read(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(and_(Notification.user_id == user_id, Notification.is_read == False))
        .values(is_read=True)
    )
    await db.commit()
    return StandardResponse(message="Todas las notificaciones marcadas como leídas")
