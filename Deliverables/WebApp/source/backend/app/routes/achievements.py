"""Tutunaku - Rutas de Logros"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id, require_admin
from app.models.mysql_models import Achievement, UserAchievement
from app.schemas.schemas import AchievementResponse, UserAchievementResponse, StandardResponse

router = APIRouter()

@router.get("", response_model=list[AchievementResponse])
async def list_achievements(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Achievement))
    return result.scalars().all()

@router.get("/me", response_model=list[UserAchievementResponse])
async def my_achievements(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(UserAchievement)
        .options(selectinload(UserAchievement.achievement))
        .where(UserAchievement.user_id == user_id)
    )
    return result.scalars().all()
