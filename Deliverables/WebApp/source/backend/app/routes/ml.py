"""
Tutunaku - API Inteligente (/api/ml)
Expone los modelos de Machine Learning entrenados en /notebooks como
endpoints REST. No modifica ninguna ruta ni lógica de /api/v1 existente.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
import structlog

from app.core.security import require_admin, require_user
from app.ml import service
from app.ml.model_registry import get_registry
from app.sockets.server import (
    emit_anomaly_alert,
    emit_new_prediction,
    run_platform_load_update_job,
    run_user_progress_update_job,
)
from app.ml.schemas import (
    AnalyzeNavigationRequest,
    AnalyzeNavigationResponse,
    DetectAnomalyRequest,
    DetectAnomalyResponse,
    MLInferenceRecord,
    MLModelInfo,
    PlatformLoadForecastResponse,
    PredictSuccessRequest,
    PredictSuccessResponse,
    PredictTimeRequest,
    PredictTimeResponse,
    SegmentUserRequest,
    SegmentUserResponse,
)

router = APIRouter()
logger = structlog.get_logger()


def _jsonable(result: dict) -> dict:
    """Convierte campos datetime del resultado de servicio a ISO string para Socket.IO."""
    out = dict(result)
    if isinstance(out.get("inference_date"), datetime):
        out["inference_date"] = out["inference_date"].isoformat()
    return out


async def _safe_emit(emit_fn, payload: dict) -> None:
    """Emitir por Socket.IO nunca debe tumbar la respuesta HTTP si falla."""
    try:
        await emit_fn(payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("ml_socket_emit_failed", error=str(exc))


@router.get("/health")
async def ml_health():
    """Estado de carga de cada modelo (no requiere autenticación, uso operativo)."""
    registry = get_registry()
    models = registry.all_info()
    return {
        "status": "ok" if any(m.loaded for m in models) else "degraded",
        "models": {m.name: {"loaded": m.loaded, "error": m.error} for m in models},
    }


@router.get("/models", response_model=list[MLModelInfo])
async def list_models(_user=Depends(require_user)):
    """Catálogo de modelos disponibles con su versión y métricas de evaluación."""
    registry = get_registry()
    info = []
    for m in registry.all_info():
        meta = m.metadata or {}
        info.append(
            MLModelInfo(
                model_name=m.name,
                version=meta.get("version", "unknown"),
                algorithm=meta.get("algorithm", "unknown"),
                task=meta.get("task", "unknown"),
                metrics=meta.get("metrics", {}),
                trained_at=meta.get("trained_at"),
                loaded=m.loaded,
                error=m.error,
            )
        )
    return info


@router.get("/inferences", response_model=list[MLInferenceRecord])
async def list_inferences(limit: int = Query(50, ge=1, le=200), _admin=Depends(require_admin)):
    """Historial de inferencias registradas (para auditoría/dashboard)."""
    return service.get_recent_inferences(limit=limit)


@router.post("/predict-time", response_model=PredictTimeResponse)
async def predict_time(payload: PredictTimeRequest, _user=Depends(require_user)):
    """S02 - Estima el tiempo de respuesta (segundos) de un intento de ejercicio."""
    result = await service.predict_time(payload)
    await _safe_emit(emit_new_prediction, {"endpoint": "predict-time", **_jsonable(result)})
    return result


@router.post("/predict-success", response_model=PredictSuccessResponse)
async def predict_success(payload: PredictSuccessRequest, _user=Depends(require_user)):
    """S06 - Predice si el usuario completará el reto conservando vidas."""
    result = await service.predict_success(payload)
    await _safe_emit(emit_new_prediction, {"endpoint": "predict-success", **_jsonable(result)})
    return result


@router.post("/detect-anomaly", response_model=DetectAnomalyResponse)
async def detect_anomaly(payload: DetectAnomalyRequest, _admin=Depends(require_admin)):
    """U04 - Detecta comportamiento sospechoso en la ganancia de XP."""
    result = await service.detect_anomaly(payload)
    if result["is_anomaly"]:
        await _safe_emit(emit_anomaly_alert, _jsonable(result))
    return result


@router.post("/segment-user", response_model=SegmentUserResponse)
async def segment_user(payload: SegmentUserRequest, _admin=Depends(require_admin)):
    """U07 - Segmenta a un usuario por compromiso (RFM + K-Means)."""
    return await service.segment_user(payload)


@router.get("/platform-load-forecast", response_model=PlatformLoadForecastResponse)
async def platform_load_forecast(
    horizon_hours: int = Query(6, ge=1, le=24), _admin=Depends(require_admin),
):
    """S08 - Pronóstico de peticiones/minuto para las próximas horas."""
    return await service.forecast_platform_load(horizon_hours=horizon_hours)


@router.post("/analyze-navigation", response_model=AnalyzeNavigationResponse)
async def analyze_navigation(payload: AnalyzeNavigationRequest, _admin=Depends(require_admin)):
    """U08 - Próximas páginas más probables y riesgo de abandono (cadena de Markov)."""
    return await service.analyze_navigation(payload)


# ============================================
# Disparo manual de los jobs periódicos (demo/depuración del dashboard):
# el dashboard normalmente los recibe solos cada N segundos, pero estos
# endpoints permiten forzar un evento de inmediato sin esperar.
# ============================================
@router.post("/trigger/platform-load-update")
async def trigger_platform_load_update(_admin=Depends(require_admin)):
    await run_platform_load_update_job()
    return {"status": "emitted", "event": "platform_load_update"}


@router.post("/trigger/user-progress-update")
async def trigger_user_progress_update(_admin=Depends(require_admin)):
    await run_user_progress_update_job()
    return {"status": "emitted", "event": "user_progress_update"}
