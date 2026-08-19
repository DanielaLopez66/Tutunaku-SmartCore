"""
Tutunaku - Schemas Pydantic (DTOs)
Validación de entrada/salida para todos los endpoints
"""
import re
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================
# RESPUESTA ESTÁNDAR
# ============================================
class StandardResponse(BaseModel):
    """Esquema de respuesta estándar para la API."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


# ============================================
# AUTH SCHEMAS
# ============================================
class RegisterRequest(BaseModel):
    """Solicitud para registro de nuevo usuario."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=150)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida que la contraseña cumpla con criterios de seguridad."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class LoginRequest(BaseModel):
    """Solicitud para inicio de sesión."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Respuesta con tokens JWT de acceso y renovación."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshTokenRequest(BaseModel):
    """Solicitud para renovar el access_token."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Solicitud para recuperar contraseña por email con CAPTCHA."""
    email: EmailStr
    captcha_id: str = Field(..., description="ID del CAPTCHA generado")
    captcha_answer: str = Field(..., description="Respuesta del usuario al CAPTCHA")


class ResetPasswordRequest(BaseModel):
    """Solicitud para establecer nueva contraseña con token."""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Solicitud para cambiar contraseña (autenticado)."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============================================
# USER SCHEMAS
# ============================================
class UserPublic(BaseModel):
    """Información pública del perfil de usuario."""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    xp_total: int
    level: int
    hearts: int
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    is_active: bool
    last_heart_refill: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Solicitud para actualizar perfil de usuario."""
    full_name: Optional[str] = Field(None, max_length=150)
    avatar_url: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserStats(BaseModel):
    """Estadísticas detalladas de progreso del usuario."""
    xp_total: int
    level: int
    hearts: int
    current_streak: int
    longest_streak: int
    lessons_completed: int
    exercises_correct: int
    exercises_total: int
    accuracy_percentage: float
    achievements_count: int
    last_heart_refill: Optional[datetime] = None


class LeaderboardEntry(BaseModel):
    """Una fila de la tabla de posiciones (top usuarios por XP)."""
    rank: int
    id: str
    username: str
    avatar_url: Optional[str] = None
    xp_total: int
    level: int
    current_streak: int
    is_me: bool = False


# ============================================
# COURSE SCHEMAS
# ============================================
class CourseCreate(BaseModel):
    """Solicitud para crear un nuevo curso."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    color_hex: str = "#FF6B6B"
    difficulty: str = "beginner"
    is_published: bool = False
    order_index: int = 0


class CourseUpdate(BaseModel):
    """Solicitud para actualizar un curso."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    color_hex: Optional[str] = None
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None
    order_index: Optional[int] = None


class CourseResponse(BaseModel):
    """Respuesta con información detallada de un curso."""
    id: str
    title: str
    description: Optional[str]
    cover_image_url: Optional[str]
    color_hex: str
    difficulty: str
    is_published: bool
    order_index: int
    created_at: datetime
    units_count: int = 0

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# LESSON SCHEMAS
# ============================================
class LessonContentBlock(BaseModel):
    """Bloque de contenido educativo dentro de una lección."""
    type: str  # text, video, audio, image, example
    content: str
    language: Optional[str] = None  # es / toto (totonaco)
    caption: Optional[str] = None
    pronunciation: Optional[str] = None
    example_sentence: Optional[str] = None


class LessonCreate(BaseModel):
    """Solicitud para crear una lección."""
    unit_id: str
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    order_index: int = 0
    xp_reward: int = 20
    content_type: Optional[str] = None
    content_data: Optional[List[LessonContentBlock]] = None
    is_published: bool = False


class LessonResponse(BaseModel):
    """Respuesta con información detallada de una lección."""
    id: str
    unit_id: str
    title: str
    description: Optional[str]
    order_index: int
    xp_reward: int
    content_type: Optional[str]
    content_data: Optional[Any]
    is_published: bool
    exercises_count: int = 0

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# UNIT SCHEMAS
# ============================================
class UnitCreate(BaseModel):
    """Solicitud para crear una unidad temática."""
    course_id: str
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    icon_emoji: str = "book-open"
    color_hex: str = "#FF6B6B"
    order_index: int = 0
    is_locked: bool = True
    xp_reward: int = 50


class UnitUpdate(BaseModel):
    """Solicitud para actualizar una unidad."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    icon_emoji: Optional[str] = None
    color_hex: Optional[str] = None
    order_index: Optional[int] = None
    is_locked: Optional[bool] = None
    xp_reward: Optional[int] = None


class UnitResponse(BaseModel):
    """Respuesta con información de una unidad."""
    id: str
    course_id: str
    title: str
    description: Optional[str]
    icon_emoji: str
    color_hex: str
    order_index: int
    is_locked: bool
    xp_reward: int
    created_at: datetime
    lessons_count: int = 0

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# EXERCISE SCHEMAS
# ============================================
class ExerciseCreate(BaseModel):
    """Solicitud para crear un ejercicio interactivo."""
    lesson_id: str
    type: str  # translation | multiple_choice | writing | audio
    question: str = Field(..., min_length=1)
    correct_answer: str = Field(..., min_length=1)
    options: Optional[List[str]] = None
    hint: Optional[str] = None
    explanation: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    xp_reward: int = Field(5, ge=1, le=100)
    order_index: int = 0


class ExerciseResponse(BaseModel):
    """Respuesta con información de un ejercicio (sin respuesta correcta)."""
    id: str
    lesson_id: str
    type: str
    question: str
    options: Optional[List[str]]
    hint: Optional[str]
    image_url: Optional[str]
    audio_url: Optional[str]
    xp_reward: int
    order_index: int

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


class ExerciseAttemptRequest(BaseModel):
    """Solicitud para enviar un intento de ejercicio."""
    user_answer: str = Field(..., min_length=1)
    time_spent_seconds: Optional[int] = Field(None, ge=0, le=3600)


class ExerciseAttemptResponse(BaseModel):
    """Resultado de un intento de ejercicio."""
    is_correct: bool
    correct_answer: str  # Solo se revela después del intento
    explanation: Optional[str]
    xp_earned: int
    hearts_remaining: int
    user_stats: Optional[dict] = None


class WordOfDayResponse(BaseModel):
    """Palabra del día en totonaco (pensada para el wearable)."""
    word: str
    translation: str
    hint: Optional[str] = None
    audio_url: Optional[str] = None
    date: str


# ============================================
# ACHIEVEMENT SCHEMAS
# ============================================
class AchievementResponse(BaseModel):
    """Respuesta con información de un logro o medalla."""
    id: str
    title: str
    description: Optional[str]
    icon_emoji: str
    badge_color: str
    xp_reward: int
    condition_type: Optional[str]
    condition_value: Optional[int]

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


class UserAchievementResponse(BaseModel):
    """Relación de un logro obtenido por un usuario."""
    achievement: AchievementResponse
    earned_at: datetime

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# NOTIFICATION SCHEMAS
# ============================================
class NotificationResponse(BaseModel):
    """Respuesta con información de una notificación de usuario."""
    id: str
    type: str
    title: str
    message: Optional[str]
    icon_emoji: Optional[str]
    is_read: bool
    action_url: Optional[str]
    created_at: datetime

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# REMINDER SCHEMAS
# ============================================
class ReminderCreate(BaseModel):
    """Solicitud para crear un recordatorio de estudio."""
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    timezone: str = "America/Mexico_City"
    message: Optional[str] = Field(None, max_length=300)
    days_of_week: List[int] = Field(default=[0, 1, 2, 3, 4, 5, 6])  # Todos los días

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: List[int]) -> List[int]:
        """Valida que los días de la semana sean válidos (0-6)."""
        if not all(0 <= d <= 6 for d in v):
            raise ValueError("Los días deben ser entre 0 (lunes) y 6 (domingo)")
        return v


class ReminderUpdate(BaseModel):
    """Solicitud para actualizar un recordatorio."""
    hour: Optional[int] = Field(None, ge=0, le=23)
    minute: Optional[int] = Field(None, ge=0, le=59)
    timezone: Optional[str] = None
    message: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    is_active: Optional[bool] = None


class ReminderResponse(BaseModel):
    """Respuesta con información de un recordatorio."""
    id: str
    hour: int
    minute: int
    timezone: str
    message: str
    days_of_week: List[int]
    is_active: bool
    last_sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        """Configuración de Pydantic."""
        from_attributes = True


# ============================================
# ADMIN SCHEMAS
# ============================================
class AdminMetrics(BaseModel):
    """Estadísticas y métricas generales del sistema para administración."""
    total_users: int
    active_users_7d: int
    total_courses: int
    total_lessons: int
    avg_completion_percentage: float
    total_exercise_attempts: int
    correct_attempts_percentage: float
    most_common_errors: List[dict]
    progress_by_lesson: List[dict]
    new_users_30d: int
    daily_active_users: List[dict]


class AdminUserUpdate(BaseModel):
    """Solicitud de administrador para modificar a un usuario."""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    xp_total: Optional[int] = None
