"""
Tutunaku - Modelos SQLAlchemy para MySQL
16 tablas con relaciones, índices y constraints
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, Float,
    DateTime, ForeignKey, Enum, JSON, Index, UniqueConstraint,
    SmallInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from app.core.base import Base


def generate_uuid():
    return str(uuid.uuid4())


# ============================================
# ENUMS
# ============================================
# pylint: disable=invalid-name
class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema."""
    admin = "admin"
    user = "user"
    visitor = "visitor"


class ExerciseType(str, enum.Enum):
    """Tipos de ejercicios interactivos soportados."""
    translation = "translation"       # Español → Totonaco
    multiple_choice = "multiple_choice"
    writing = "writing"
    audio = "audio"


class DifficultyLevel(str, enum.Enum):
    """Niveles de dificultad para cursos."""
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class NotificationType(str, enum.Enum):
    """Categorías de notificaciones del sistema."""
    reminder = "reminder"
    achievement = "achievement"
    progress = "progress"
    system = "system"


# ============================================
# TABLA: users
# ============================================
class User(Base):
    """Modelo de usuario con datos de perfil y gamificación."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150))
    avatar_url = Column(String(500))
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    
    # Gamificación
    xp_total = Column(Integer, default=0)
    level = Column(SmallInteger, default=1)
    hearts = Column(SmallInteger, default=5)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_heart_refill = Column(DateTime(timezone=True))
    last_activity_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="user", cascade="all, delete-orphan")
    daily_streaks = relationship("DailyStreak", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


# ============================================
# TABLA: courses
# ============================================
class Course(Base):
    """Modelo de curso educativo."""
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    cover_image_url = Column(String(500))
    color_hex = Column(String(7), default='#FF6B6B')  # Color for the course
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.beginner)
    is_published = Column(Boolean, default=False)
    order_index = Column(SmallInteger, default=0)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan", order_by="Unit.order_index")
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (Index("idx_courses_published", "is_published"),)


# ============================================
# TABLA: units
# ============================================
class Unit(Base):
    """Modelo de unidad temática dentro de un curso."""
    __tablename__ = "units"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    icon_emoji = Column(String(10), default="book-open")
    color_hex = Column(String(7), default="#FF6B6B")
    order_index = Column(SmallInteger, default=0)
    is_locked = Column(Boolean, default=True)
    xp_reward = Column(Integer, default=50)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    course = relationship("Course", back_populates="units")
    lessons = relationship("Lesson", back_populates="unit", cascade="all, delete-orphan", order_by="Lesson.order_index")

    __table_args__ = (Index("idx_units_course", "course_id"),)


# ============================================
# TABLA: lessons
# ============================================
class Lesson(Base):
    """Modelo de lección educativa."""
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    unit_id = Column(String(36), ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order_index = Column(SmallInteger, default=0)
    xp_reward = Column(Integer, default=20)
    
    # Contenido educativo (clase antes del ejercicio)
    content_type = Column(String(50))  # text, video, audio, mixed
    content_data = Column(JSON)         # Contenido estructurado (texto, URLs, etc.)
    
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    unit = relationship("Unit", back_populates="lessons")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan", order_by="Exercise.order_index")
    progress = relationship("UserProgress", back_populates="lesson")

    __table_args__ = (Index("idx_lessons_unit", "unit_id"),)


# ============================================
# TABLA: exercises
# ============================================
class Exercise(Base):
    """Modelo de ejercicio interactivo dentro de una lección."""
    __tablename__ = "exercises"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(ExerciseType), nullable=False)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    options = Column(JSON)              # Para selección múltiple
    hint = Column(Text)
    explanation = Column(Text)          # Explicación de la respuesta correcta
    audio_url = Column(String(500))     # Para ejercicios de audio
    image_url = Column(String(500))
    xp_reward = Column(Integer, default=5)
    order_index = Column(SmallInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    lesson = relationship("Lesson", back_populates="exercises")
    attempts = relationship("ExerciseAttempt", back_populates="exercise")

    __table_args__ = (Index("idx_exercises_lesson", "lesson_id"),)


# ============================================
# TABLA: exercise_attempts
# ============================================
class ExerciseAttempt(Base):
    """Modelo de registro de intentos de ejercicios por usuarios."""
    __tablename__ = "exercise_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(String(36), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    xp_earned = Column(Integer, default=0)
    time_spent_seconds = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="attempts")

    __table_args__ = (
        Index("idx_attempts_user", "user_id"),
        Index("idx_attempts_exercise", "exercise_id"),
    )


# ============================================
# TABLA: user_progress
# ============================================
class UserProgress(Base):
    """Modelo de progreso acumulado del usuario en lecciones."""
    __tablename__ = "user_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    attempts_count = Column(Integer, default=0)
    xp_earned = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
        Index("idx_progress_user", "user_id"),
    )


# ============================================
# TABLA: achievements (insignias disponibles)
# ============================================
class Achievement(Base):
    """Modelo de logros e insignias disponibles en la plataforma."""
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    icon_url = Column(String(500))
    icon_emoji = Column(String(10), default="trophy")
    badge_color = Column(String(7), default="#FFD700")
    xp_reward = Column(Integer, default=100)
    
    # Condición para obtenerla (JSON con reglas)
    condition_type = Column(String(50))   # streak, xp, lessons, perfect_score, etc.
    condition_value = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user_achievements = relationship("UserAchievement", back_populates="achievement")


# ============================================
# TABLA: user_achievements
# ============================================
class UserAchievement(Base):
    """Relación de muchos a muchos entre usuarios y sus logros ganados."""
    __tablename__ = "user_achievements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(String(36), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )


# ============================================
# TABLA: daily_streaks
# ============================================
class DailyStreak(Base):
    """Modelo para rastrear la racha diaria de actividad de los usuarios."""
    __tablename__ = "daily_streaks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    streak_date = Column(DateTime(timezone=True), nullable=False)
    xp_earned_today = Column(Integer, default=0)
    lessons_completed_today = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="daily_streaks")

    __table_args__ = (
        UniqueConstraint("user_id", "streak_date", name="uq_user_streak_date"),
        Index("idx_streaks_user", "user_id"),
    )


# ============================================
# TABLA: refresh_tokens
# ============================================
class RefreshToken(Base):
    """Modelo para el manejo de sesiones persistentes con refresh tokens."""
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (Index("idx_refresh_tokens_user", "user_id"),)


# ============================================
# TABLA: password_resets
# ============================================
class PasswordReset(Base):
    """Modelo para tokens de recuperación de contraseñas olvidadas."""
    __tablename__ = "password_resets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="password_resets")


# ============================================
# TABLA: email_verifications
# ============================================
class EmailVerification(Base):
    """Modelo para tokens de verificación de correo electrónico."""
    __tablename__ = "email_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="email_verifications")


# ============================================
# TABLA: notifications
# ============================================
class Notification(Base):
    """Modelo de notificaciones push/in-app para usuarios."""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    icon_emoji = Column(String(10))
    is_read = Column(Boolean, default=False)
    action_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="notifications")

    __table_args__ = (Index("idx_notifications_user_unread", "user_id", "is_read"),)


# ============================================
# TABLA: reminders
# ============================================
class Reminder(Base):
    """Modelo para recordatorios de estudio personalizables por el usuario."""
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hour = Column(SmallInteger, nullable=False)    # 0-23
    minute = Column(SmallInteger, nullable=False)  # 0-59
    timezone = Column(String(50), default="America/Mexico_City")
    is_active = Column(Boolean, default=True)
    message = Column(String(300), default="¡Es hora de estudiar totonaco!")
    days_of_week = Column(JSON)  # [0,1,2,3,4,5,6] = lun-dom
    last_sent_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="reminders")

    __table_args__ = (Index("idx_reminders_user", "user_id"),)
