"""
Tutunaku - Rutas de Ejercicios
Sistema de gamificación: XP, corazones, rachas, logros
"""
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from datetime import datetime, timezone, date
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id, require_admin
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.mysql_models import (
    Exercise, ExerciseAttempt, ExerciseType, User, UserProgress, Lesson,
    DailyStreak, Achievement, UserAchievement, Notification
)
from app.schemas.schemas import (
    ExerciseResponse, ExerciseAttemptRequest, ExerciseAttemptResponse,
    StandardResponse, ExerciseCreate, WordOfDayResponse
)

router = APIRouter()
logger = structlog.get_logger()

# Configuración de gamificación
XP_PER_CORRECT = 10
XP_MULTIPLIER_PERFECT = 1.5
HEARTS_LOSS_ON_WRONG = 1
MIN_HEARTS = 0
MAX_HEARTS = 5
HEARTS_REGEN_HOURS = 1


# ============================================
# GET /exercises/{lesson_id}
# ============================================
@router.get("/lesson/{lesson_id}", response_model=list[ExerciseResponse])
async def get_exercises_by_lesson(
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Obtiene los ejercicios de una lección."""
    result = await db.execute(
        select(Exercise)
        .where(Exercise.lesson_id == lesson_id)
        .order_by(Exercise.order_index)
    )
    exercises = result.scalars().all()
    return exercises


# ============================================
# GET /exercises/word-of-day
# ============================================
@router.get("/word-of-day", response_model=WordOfDayResponse)
async def get_word_of_day(db: AsyncSession = Depends(get_db)):
    """Palabra del día en totonaco, estable durante el día (pensada para el wearable)."""
    result = await db.execute(select(Exercise).where(Exercise.type == ExerciseType.translation))
    candidates = result.scalars().all()
    if not candidates:
        result = await db.execute(select(Exercise))
        candidates = result.scalars().all()
    if not candidates:
        raise NotFoundError("Ejercicios")

    today = date.today().isoformat()
    ordered = sorted(candidates, key=lambda e: e.id)  # orden estable entre llamadas
    index = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(ordered)
    chosen = ordered[index]

    return WordOfDayResponse(
        word=chosen.correct_answer,
        translation=chosen.question,
        hint=chosen.hint,
        audio_url=chosen.audio_url,
        date=today,
    )


# ============================================
# POST /exercises/{exercise_id}/attempt
# ============================================
@router.post("/{exercise_id}/attempt", response_model=ExerciseAttemptResponse)
async def submit_attempt(
    exercise_id: str,
    data: ExerciseAttemptRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Procesa una respuesta del usuario con lógica de gamificación completa."""

    # 1. Obtener ejercicio
    ex_result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = ex_result.scalar_one_or_none()
    if not exercise:
        raise NotFoundError("Ejercicio")

    # 2. Obtener usuario
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario")

    # Regenerate hearts before checking
    await regenerate_hearts_if_needed(db, user)

    # 3. Verificar corazones (no puede continuar si tiene 0 corazones)
    if user.hearts <= MIN_HEARTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "NO_HEARTS",
                "message": "No tienes corazones disponibles. Espera para que se regeneren.",
                "hearts": 0,
            },
        )

    # 4. Evaluar respuesta
    is_correct = evaluate_answer(
        exercise_type=exercise.type.value,
        user_answer=data.user_answer.strip(),
        correct_answer=exercise.correct_answer.strip(),
    )

    # 5. Calcular XP ganado
    xp_earned = exercise.xp_reward if is_correct else 0

    # 6. Actualizar corazones
    if not is_correct:
        if user.hearts == MAX_HEARTS:
            user.last_heart_refill = datetime.now(timezone.utc)
        user.hearts = max(MIN_HEARTS, user.hearts - HEARTS_LOSS_ON_WRONG)

    # 7. Actualizar XP del usuario si es correcto
    new_xp_record = False
    previous_global_max_xp = 0
    if is_correct:
        # Se consulta el máximo global ANTES de sumar el XP de este intento,
        # para saber si este usuario está a punto de convertirse en el nuevo #1.
        max_xp_result = await db.execute(select(func.max(User.xp_total)))
        previous_global_max_xp = max_xp_result.scalar() or 0

        user.xp_total += xp_earned
        new_level = calculate_level(user.xp_total)
        if new_level > user.level:
            user.level = new_level
            await create_notification(
                db, user_id,
                "achievement",
                f"¡Subiste al nivel {new_level}!",
                f"Ahora eres nivel {new_level}. ¡Sigue aprendiendo!",
                "arrow-up"
            )
        if user.xp_total > previous_global_max_xp:
            new_xp_record = True

    # 8. Registrar intento
    attempt = ExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=data.user_answer,
        is_correct=is_correct,
        xp_earned=xp_earned,
        time_spent_seconds=data.time_spent_seconds,
    )
    db.add(attempt)

    # 9. Actualizar racha diaria
    await update_daily_streak(db, user)

    # 10. Verificar logros
    await check_and_award_achievements(db, user)

    await db.commit()

    logger.info(
        "exercise_attempt",
        user_id=user_id,
        exercise_id=exercise_id,
        is_correct=is_correct,
        xp_earned=xp_earned,
    )

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
    except Exception as exc:  # noqa: BLE001 - el intento nunca debe fallar por esto
        logger.warning("user_stats_updated_emit_failed", error=str(exc))

    if new_xp_record:
        try:
            from app.sockets.server import emit_admin_xp_record
            await emit_admin_xp_record({
                "user_id": user.id,
                "username": user.username,
                "xp_total": user.xp_total,
                "previous_record": previous_global_max_xp,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:  # noqa: BLE001 - el intento nunca debe fallar por esto
            logger.warning("admin_xp_record_emit_failed", error=str(exc))

    return ExerciseAttemptResponse(
        is_correct=is_correct,
        correct_answer=exercise.correct_answer,
        explanation=exercise.explanation,
        xp_earned=xp_earned,
        hearts_remaining=user.hearts,
        user_stats={
            "xp_total": user.xp_total,
            "level": user.level,
            "current_streak": user.current_streak,
        },
    )


# ============================================
# POST /exercises
# ============================================
@router.post("", response_model=StandardResponse, status_code=201)
async def create_exercise(
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Crea un nuevo ejercicio (solo admin)."""
    from app.schemas.schemas import ExerciseCreate
    from app.models.mysql_models import Exercise

    exercise_data = ExerciseCreate(**data)
    exercise = Exercise(**exercise_data.model_dump())
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return StandardResponse(message="Ejercicio creado", data={"id": exercise.id})


# ============================================
# LÓGICA DE GAMIFICACIÓN
# ============================================

async def regenerate_hearts_if_needed(db: AsyncSession, user: User):
    """Regenerates hearts based on time passed."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    
    if user.hearts < MAX_HEARTS:
        if not user.last_heart_refill:
            user.last_heart_refill = now
            return
            
        last_refill = user.last_heart_refill
        if last_refill.tzinfo is None:
            last_refill = last_refill.replace(tzinfo=timezone.utc)
            
        hours_passed = (now - last_refill).total_seconds() / 3600.0
        
        if hours_passed >= HEARTS_REGEN_HOURS:
            hearts_to_add = int(hours_passed // HEARTS_REGEN_HOURS)
            new_hearts = min(MAX_HEARTS, user.hearts + hearts_to_add)
            
            if new_hearts > user.hearts:
                user.hearts = new_hearts
                if user.hearts == MAX_HEARTS:
                    user.last_heart_refill = None
                else:
                    user.last_heart_refill = last_refill + timedelta(hours=hearts_to_add * HEARTS_REGEN_HOURS)

def evaluate_answer(exercise_type: str, user_answer: str, correct_answer: str) -> bool:
    """Evalúa si la respuesta es correcta según el tipo de ejercicio."""
    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()

    if exercise_type == "translation":
        # Para traducciones, toleramos variaciones menores
        return user_clean == correct_clean or levenshtein_distance(user_clean, correct_clean) <= 1

    elif exercise_type == "multiple_choice":
        return user_clean == correct_clean

    elif exercise_type == "writing":
        return user_clean == correct_clean

    elif exercise_type == "audio":
        # Para audio, comparar con transcripción
        return user_clean == correct_clean

    return user_clean == correct_clean


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula distancia de edición entre dos strings (tolerancia tipográfica)."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def calculate_level(xp_total: int) -> int:
    """Calcula el nivel del usuario basado en XP total."""
    # Fórmula: cada nivel requiere más XP
    # Nivel 1: 0 XP, Nivel 2: 100 XP, Nivel 3: 250 XP, etc.
    level = 1
    required_xp = 0
    increment = 100
    while xp_total >= required_xp + increment:
        required_xp += increment
        increment = int(increment * 1.5)
        level += 1
    return min(level, 50)  # Máximo nivel 50


async def update_daily_streak(db: AsyncSession, user: User):
    """Actualiza la racha diaria del usuario."""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

    # Verificar si ya hay entrada hoy
    streak_result = await db.execute(
        select(DailyStreak).where(
            and_(
                DailyStreak.user_id == user.id,
                DailyStreak.streak_date >= today_start,
            )
        )
    )
    today_streak = streak_result.scalar_one_or_none()

    if not today_streak:
        # Primera actividad del día
        yesterday_start = datetime.combine(
            date.fromordinal(today.toordinal() - 1),
            datetime.min.time()
        ).replace(tzinfo=timezone.utc)

        yesterday_result = await db.execute(
            select(DailyStreak).where(
                and_(
                    DailyStreak.user_id == user.id,
                    DailyStreak.streak_date >= yesterday_start,
                    DailyStreak.streak_date < today_start,
                )
            )
        )
        yesterday_streak = yesterday_result.scalar_one_or_none()

        if yesterday_streak:
            user.current_streak += 1
        else:
            user.current_streak = 1

        user.longest_streak = max(user.longest_streak, user.current_streak)

        new_streak = DailyStreak(
            user_id=user.id,
            streak_date=today_start,
            xp_earned_today=0,
            lessons_completed_today=0,
        )
        db.add(new_streak)

    user.last_activity_date = datetime.now(timezone.utc)


async def check_and_award_achievements(db: AsyncSession, user: User):
    """Verifica y otorga logros según condiciones."""
    # Obtener logros ya ganados por el usuario
    earned_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    earned_ids = {row[0] for row in earned_result.all()}

    # Obtener todos los logros disponibles
    all_achievements_result = await db.execute(select(Achievement))
    all_achievements = all_achievements_result.scalars().all()

    for achievement in all_achievements:
        if achievement.id in earned_ids:
            continue

        # Verificar condición
        should_award = False

        if achievement.condition_type == "streak":
            should_award = user.current_streak >= achievement.condition_value

        elif achievement.condition_type == "xp":
            should_award = user.xp_total >= achievement.condition_value

        elif achievement.condition_type == "level":
            should_award = user.level >= achievement.condition_value

        if should_award:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
            )
            db.add(user_achievement)
            user.xp_total += achievement.xp_reward

            await create_notification(
                db, user.id,
                "achievement",
                f"¡Nuevo logro: {achievement.title}!",
                achievement.description or "",
                achievement.icon_emoji,
            )


async def create_notification(
    db: AsyncSession,
    user_id: str,
    notif_type: str,
    title: str,
    message: str,
    icon_emoji: str = "bell",
    action_url: str | None = None,
):
    """Crea una notificación para el usuario y la empuja en vivo (web + wearable)."""
    from app.models.mysql_models import generate_uuid

    # El id se genera aquí explícitamente (en vez de confiar en el default de
    # la columna, que SQLAlchemy solo aplica hasta el flush) para poder
    # incluirlo en el evento en vivo sin esperar al commit del caller.
    notif_id = generate_uuid()
    notif = Notification(
        id=notif_id,
        user_id=user_id,
        type=notif_type,
        title=title,
        message=message,
        icon_emoji=icon_emoji,
        action_url=action_url,
    )
    db.add(notif)

    try:
        from app.sockets.server import emit_new_notification
        await emit_new_notification(user_id, {
            "id": notif_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "icon_emoji": icon_emoji,
            "action_url": action_url,
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as exc:  # noqa: BLE001 - crear la notificación nunca debe fallar por esto
        logger.warning("new_notification_emit_failed", error=str(exc))
