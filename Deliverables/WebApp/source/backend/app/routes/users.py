"""Tutunaku - Rutas de Usuarios"""
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.exceptions import NotFoundError
from app.models.mysql_models import User, UserProgress, ExerciseAttempt, UserAchievement
from app.schemas.schemas import UserPublic, UserStats, UserUpdateRequest, StandardResponse, LeaderboardEntry
from app.routes.exercises import regenerate_hearts_if_needed, MAX_HEARTS

router = APIRouter()
logger = structlog.get_logger()


@router.get("/me", response_model=UserPublic)
async def get_me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """Perfil del usuario autenticado."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")
        
    await regenerate_hearts_if_needed(db, user)
    await db.commit()
    
    # Ensure streaks are not None
    if user.current_streak is None:
        user.current_streak = 0
    if user.longest_streak is None:
        user.longest_streak = 0
    return user


@router.patch("/me", response_model=StandardResponse)
async def update_me(
    data: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza el perfil del usuario."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    await db.commit()
    return StandardResponse(message="Perfil actualizado")


async def _build_user_stats(db: AsyncSession, user: User) -> UserStats:
    """Ensambla UserStats a partir de un User ya cargado. Compartido por
    /me/stats y /me/hearts/earn para no duplicar las mismas 4 consultas."""
    lessons_result = await db.execute(
        select(func.count(UserProgress.id)).where(
            UserProgress.user_id == user.id, UserProgress.is_completed == True
        )
    )
    lessons_completed = lessons_result.scalar() or 0

    total_ex_result = await db.execute(
        select(func.count(ExerciseAttempt.id)).where(ExerciseAttempt.user_id == user.id)
    )
    total_exercises = total_ex_result.scalar() or 0

    correct_ex_result = await db.execute(
        select(func.count(ExerciseAttempt.id)).where(
            ExerciseAttempt.user_id == user.id, ExerciseAttempt.is_correct == True
        )
    )
    correct_exercises = correct_ex_result.scalar() or 0

    achievements_result = await db.execute(
        select(func.count(UserAchievement.id)).where(UserAchievement.user_id == user.id)
    )
    achievements_count = achievements_result.scalar() or 0

    accuracy = (correct_exercises / total_exercises * 100) if total_exercises > 0 else 0.0

    return UserStats(
        xp_total=user.xp_total,
        level=user.level,
        hearts=user.hearts,
        current_streak=user.current_streak or 0,
        longest_streak=user.longest_streak or 0,
        lessons_completed=lessons_completed,
        exercises_correct=correct_exercises,
        exercises_total=total_exercises,
        accuracy_percentage=round(accuracy, 2),
        achievements_count=achievements_count,
    )


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """Estadísticas del usuario."""
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    await regenerate_hearts_if_needed(db, user)
    await db.commit()

    return await _build_user_stats(db, user)


@router.post("/me/hearts/earn", response_model=UserStats)
async def earn_heart(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """
    Otorga 1 vida como recompensa de un minijuego (p. ej. el del wearable al
    tocar el corazón). Tope en MAX_HEARTS: ese es su único límite de abuso,
    igual que el resto de la gamificación existente (no hay forma de superar
    el máximo, solo de recuperar más rápido lo que ya se perdió).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    await regenerate_hearts_if_needed(db, user)

    if user.hearts >= MAX_HEARTS:
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "HEARTS_FULL", "message": "Ya tienes el máximo de vidas."},
        )

    user.hearts += 1
    await db.commit()

    logger.info("heart_earned", user_id=user_id, hearts=user.hearts)

    try:
        from app.sockets.server import emit_user_stats_updated
        await emit_user_stats_updated(user_id, {
            "xp_total": user.xp_total,
            "level": user.level,
            "hearts": user.hearts,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as exc:  # noqa: BLE001 - el minijuego nunca debe fallar por esto
        logger.warning("user_stats_updated_emit_failed", error=str(exc))

    return await _build_user_stats(db, user)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Top usuarios por XP total (tabla de posiciones)."""
    limit = max(1, min(limit, 100))
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(User.xp_total.desc())
        .limit(limit)
    )
    users = result.scalars().all()
    return [
        LeaderboardEntry(
            rank=i + 1,
            id=u.id,
            username=u.username,
            avatar_url=u.avatar_url,
            xp_total=u.xp_total,
            level=u.level,
            current_streak=u.current_streak or 0,
            is_me=(u.id == user_id),
        )
        for i, u in enumerate(users)
    ]
