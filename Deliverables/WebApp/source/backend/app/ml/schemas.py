"""
Tutunaku - Esquemas Pydantic del módulo de Machine Learning (/api/ml).

Se mantienen en su propio archivo (en vez de app/schemas/schemas.py) porque
son un bloque grande y autocontenido; evita conflictos de merge con los
esquemas del resto de la aplicación, que no se tocan.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

DeviceType = Literal["mobile", "desktop", "tablet"]
NavState = Literal[
    "home", "mapa_niveles", "leccion", "ejercicio", "resultado",
    "logros", "leaderboard", "perfil", "configuracion", "salir",
]


# ============================================
# S02 - Regresión: tiempo de respuesta
# ============================================
class PredictTimeRequest(BaseModel):
    attempt_number: int = Field(ge=1, le=20, description="Número de intento sobre el mismo ejercicio")
    difficulty: int = Field(ge=1, le=5)
    connectivity_quality: float = Field(ge=0.0, le=1.0)
    device_type: DeviceType
    hour_of_day: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6, description="0=lunes ... 6=domingo")
    is_correct: bool
    hearts_before: int = Field(ge=0, le=5)


class PredictTimeResponse(BaseModel):
    predicted_time_seconds: float
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# S06 - Clasificación: éxito conservando vidas
# ============================================
class PredictSuccessRequest(BaseModel):
    difficulty: int = Field(ge=1, le=5)
    num_exercises: int = Field(ge=1, le=50)
    connectivity_quality: float = Field(ge=0.0, le=1.0)
    device_type: DeviceType
    prior_success_rate_30d: float = Field(ge=0.0, le=1.0)
    hearts_start: int = Field(ge=1, le=5)


class PredictSuccessResponse(BaseModel):
    completed_with_lives: bool
    probability: float
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# U04 - Detección de anomalías
# ============================================
class DetectAnomalyRequest(BaseModel):
    xp_gained: float = Field(ge=0)
    session_duration_seconds: float = Field(ge=0)
    seconds_since_prev_event: float = Field(ge=0)
    events_last_hour_user: int = Field(ge=0)


class DetectAnomalyResponse(BaseModel):
    is_anomaly: bool
    anomaly_score: float = Field(description="Mayor = más anómalo")
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# U07 - Segmentación RFM
# ============================================
class SegmentUserRequest(BaseModel):
    recency_days: float = Field(ge=0)
    frequency_sessions: float = Field(ge=0)
    educational_value_xp: float = Field(ge=0)


class SegmentUserResponse(BaseModel):
    cluster: int
    segment_label: str
    distance_to_centroid: float
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# S08 - Pronóstico de carga (GET, sin body)
# ============================================
class PlatformLoadForecastPoint(BaseModel):
    horizon_hours: int
    predicted_requests_per_minute: float


class PlatformLoadForecastResponse(BaseModel):
    forecast: list[PlatformLoadForecastPoint]
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# U08 - Análisis de navegación (Markov)
# ============================================
class AnalyzeNavigationRequest(BaseModel):
    current_state: NavState


class NextPageProbability(BaseModel):
    page: str
    probability: float


class AnalyzeNavigationResponse(BaseModel):
    current_state: str
    next_page_probabilities: list[NextPageProbability]
    drop_off_risk: float = Field(description="Probabilidad de abandonar (ir a 'salir') desde este estado")
    model: str
    model_version: str
    inference_date: datetime


# ============================================
# Metadatos / catálogo de modelos
# ============================================
class MLModelInfo(BaseModel):
    model_name: str
    version: str
    algorithm: str
    task: str
    metrics: dict
    trained_at: Optional[str] = None
    loaded: bool
    error: Optional[str] = None


class MLInferenceRecord(BaseModel):
    id: int
    model_name: str
    model_version: Optional[str] = None
    endpoint: str
    confidence: Optional[float] = None
    created_at: str
