"""Tutunaku - Rutas de Lecciones"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog
from app.core.database import get_db
from app.core.security import get_current_user_id, require_admin
from app.core.exceptions import NotFoundError
from app.models.mysql_models import Exercise, Lesson, User, UserProgress
from app.schemas.schemas import LessonCreate, LessonResponse, StandardResponse

router = APIRouter()
logger = structlog.get_logger()


@router.get("/unit/{unit_id}", response_model=list[LessonResponse])
async def get_lessons_by_unit(unit_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lesson).where(Lesson.unit_id == unit_id, Lesson.is_published == True)
        .order_by(Lesson.order_index)
    )
    lessons = result.scalars().all()

    counts_result = await db.execute(
        select(Exercise.lesson_id, func.count(Exercise.id)).group_by(Exercise.lesson_id)
    )
    exercises_count_by_lesson = dict(counts_result.all())

    return [LessonResponse(
        id=l.id, unit_id=l.unit_id, title=l.title, description=l.description,
        order_index=l.order_index, xp_reward=l.xp_reward,
        content_type=l.content_type, content_data=l.content_data,
        is_published=l.is_published, exercises_count=exercises_count_by_lesson.get(l.id, 0),
    ) for l in lessons]


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise NotFoundError("Lección")
    exercises_count = (await db.execute(
        select(func.count(Exercise.id)).where(Exercise.lesson_id == lesson_id)
    )).scalar_one()
    return LessonResponse(
        id=lesson.id, unit_id=lesson.unit_id, title=lesson.title,
        description=lesson.description, order_index=lesson.order_index,
        xp_reward=lesson.xp_reward, content_type=lesson.content_type,
        content_data=lesson.content_data, is_published=lesson.is_published,
        exercises_count=exercises_count,
    )


@router.post("", response_model=StandardResponse, status_code=201)
async def create_lesson(
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    lesson_data = data.model_dump()
    if lesson_data.get("content_data"):
        lesson_data["content_data"] = [b.model_dump() for b in data.content_data]
    lesson = Lesson(**lesson_data)
    db.add(lesson)
    await db.commit()
    return StandardResponse(message="Lección creada", data={"id": lesson.id})


@router.post("/{lesson_id}/complete", response_model=StandardResponse)
async def complete_lesson(
    lesson_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Marca una lección como completada y otorga su XP (solo la primera vez)."""
    from sqlalchemy import and_
    from datetime import datetime, timezone
    from app.routes.exercises import calculate_level

    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise NotFoundError("Lección")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    progress_result = await db.execute(
        select(UserProgress).where(
            and_(UserProgress.user_id == user_id, UserProgress.lesson_id == lesson_id)
        )
    )
    progress = progress_result.scalar_one_or_none()

    xp_earned = 0
    if not progress:
        # Primera vez que completa esta lección: sí otorga XP al total del usuario
        # (antes este endpoint solo registraba el progreso, sin sumar XP real).
        xp_earned = lesson.xp_reward
        user.xp_total += xp_earned
        user.level = calculate_level(user.xp_total)
        progress = UserProgress(
            user_id=user_id, lesson_id=lesson_id,
            is_completed=True, completion_percentage=100.0,
            score=100.0, xp_earned=xp_earned,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(progress)
    else:
        progress.is_completed = True
        progress.completion_percentage = 100.0
        progress.completed_at = datetime.now(timezone.utc)

    await db.commit()

    try:
        from app.sockets.server import emit_admin_lesson_completed, emit_user_stats_updated
        now_iso = datetime.now(timezone.utc).isoformat()
        await emit_admin_lesson_completed({
            "user_id": user_id,
            "username": user.username,
            "lesson_id": lesson_id,
            "lesson_title": lesson.title,
            "xp_earned": xp_earned,
            "completed_at": now_iso,
        })
        await emit_user_stats_updated(user_id, {
            "xp_total": user.xp_total,
            "level": user.level,
            "hearts": user.hearts,
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "timestamp": now_iso,
        })
    except Exception as exc:  # noqa: BLE001 - completar la lección nunca debe fallar por esto
        logger.warning("lesson_completed_emit_failed", error=str(exc))

    return StandardResponse(message="Lección completada", data={"xp_earned": xp_earned})
