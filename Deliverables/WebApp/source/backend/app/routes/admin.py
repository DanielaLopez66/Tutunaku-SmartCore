"""
Tutunaku - Rutas de Administración
Dashboard con métricas, gestión de usuarios, cursos y contenido
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta, timezone
import structlog

from app.core.database import get_db
from app.core.security import require_admin
from app.core.exceptions import NotFoundError
from app.models.mysql_models import (
    User, Course, Lesson, Exercise, ExerciseAttempt,
    UserProgress, Achievement, UserAchievement
)
from app.schemas.schemas import (
    AdminMetrics, AdminUserUpdate, CourseCreate, CourseUpdate,
    StandardResponse, UserPublic
)

router = APIRouter()
logger = structlog.get_logger()


# ============================================
# GET /admin/metrics
# ============================================
@router.get("/metrics", response_model=AdminMetrics)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Obtiene métricas globales del sistema."""
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # Total de usuarios
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    # Usuarios activos en últimos 7 días
    active_7d_result = await db.execute(
        select(func.count(User.id)).where(User.last_activity_date >= seven_days_ago)
    )
    active_users_7d = active_7d_result.scalar() or 0

    # Total cursos
    total_courses_result = await db.execute(select(func.count(Course.id)))
    total_courses = total_courses_result.scalar() or 0

    # Total lecciones
    total_lessons_result = await db.execute(select(func.count(Lesson.id)))
    total_lessons = total_lessons_result.scalar() or 0

    # Porcentaje promedio de completación
    avg_completion_result = await db.execute(
        select(func.avg(UserProgress.completion_percentage))
    )
    avg_completion = float(avg_completion_result.scalar() or 0)

    # Total intentos de ejercicios
    total_attempts_result = await db.execute(select(func.count(ExerciseAttempt.id)))
    total_attempts = total_attempts_result.scalar() or 0

    # Porcentaje de respuestas correctas
    correct_attempts_result = await db.execute(
        select(func.count(ExerciseAttempt.id)).where(ExerciseAttempt.is_correct == True)
    )
    correct_attempts = correct_attempts_result.scalar() or 0
    correct_percentage = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

    # Errores más comunes (ejercicios con más intentos incorrectos)
    most_errors_result = await db.execute(
        select(
            Exercise.question,
            func.count(ExerciseAttempt.id).label("error_count")
        )
        .join(ExerciseAttempt, Exercise.id == ExerciseAttempt.exercise_id)
        .where(ExerciseAttempt.is_correct == False)
        .group_by(Exercise.id)
        .order_by(desc("error_count"))
        .limit(5)
    )
    most_common_errors = [
        {"question": row[0], "errors": row[1]}
        for row in most_errors_result.all()
    ]

    # Progreso por lección
    progress_by_lesson_result = await db.execute(
        select(
            Lesson.title,
            func.avg(UserProgress.completion_percentage).label("avg_completion"),
            func.count(UserProgress.id).label("total_users"),
        )
        .join(UserProgress, Lesson.id == UserProgress.lesson_id)
        .group_by(Lesson.id)
        .order_by(desc("avg_completion"))
        .limit(10)
    )
    progress_by_lesson = [
        {
            "lesson": row[0],
            "avg_completion": round(float(row[1] or 0), 2),
            "users": row[2],
        }
        for row in progress_by_lesson_result.all()
    ]

    # Nuevos usuarios en 30 días
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    new_users_30d = new_users_result.scalar() or 0

    # Usuarios activos por día (últimos 7 días)
    daily_active = []
    for i in range(7):
        day_start = now - timedelta(days=i+1)
        day_end = now - timedelta(days=i)
        day_result = await db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.last_activity_date >= day_start,
                    User.last_activity_date < day_end,
                )
            )
        )
        daily_active.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "active_users": day_result.scalar() or 0,
        })

    return AdminMetrics(
        total_users=total_users,
        active_users_7d=active_users_7d,
        total_courses=total_courses,
        total_lessons=total_lessons,
        avg_completion_percentage=round(avg_completion, 2),
        total_exercise_attempts=total_attempts,
        correct_attempts_percentage=round(correct_percentage, 2),
        most_common_errors=most_common_errors,
        progress_by_lesson=progress_by_lesson,
        new_users_30d=new_users_30d,
        daily_active_users=list(reversed(daily_active)),
    )


# ============================================
# GET /admin/users
# ============================================
@router.get("/users", response_model=list[UserPublic])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Lista todos los usuarios."""
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all()


# ============================================
# PATCH /admin/users/{user_id}
# ============================================
@router.patch("/users/{user_id}", response_model=StandardResponse)
async def update_user(
    user_id: str,
    data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Actualiza datos de un usuario (admin)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.xp_total is not None:
        user.xp_total = data.xp_total

    await db.commit()
    return StandardResponse(message="Usuario actualizado")


# ============================================
# DELETE /admin/users/{user_id}/progress
# ============================================
@router.delete("/users/{user_id}/progress", response_model=StandardResponse)
async def reset_user_progress(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Reinicia el progreso de un usuario."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    # Resetear stats
    user.xp_total = 0
    user.level = 1
    user.hearts = 5
    user.current_streak = 0

    # Eliminar progreso de lecciones
    progress_result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    for p in progress_result.scalars().all():
        await db.delete(p)

    await db.commit()
    logger.info("admin_reset_user_progress", target_user_id=user_id)
    return StandardResponse(message="Progreso del usuario reiniciado")


# ============================================
# POST /admin/achievements/award
# ============================================
@router.post("/achievements/{achievement_id}/award/{user_id}", response_model=StandardResponse)
async def award_achievement(
    achievement_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Otorga una insignia manualmente a un usuario."""
    # Verificar que no la tenga ya
    existing = await db.execute(
        select(UserAchievement).where(
            and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        return StandardResponse(message="El usuario ya tiene este logro")

    ua = UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.add(ua)
    await db.commit()

    return StandardResponse(message="Logro otorgado exitosamente")
