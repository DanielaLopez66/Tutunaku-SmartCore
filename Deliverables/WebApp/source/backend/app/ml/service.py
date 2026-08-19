"""
Tutunaku - Servicio de inferencia del módulo de Machine Learning.

Convierte los esquemas Pydantic de entrada en el formato que cada pipeline de
scikit-learn (o artefacto custom, como la cadena de Markov) espera, ejecuta la
inferencia, calcula una confianza/score, y registra cada inferencia en la
tabla `fact_ml_inferences` del Data Warehouse analítico local (independiente
de la base de datos transaccional de la app).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import structlog
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.exceptions import MLInferenceError, MLModelUnavailableError
from app.ml.model_registry import LoadedModel, get_registry
from app.ml.schemas import (
    AnalyzeNavigationRequest,
    DetectAnomalyRequest,
    NextPageProbability,
    PlatformLoadForecastPoint,
    PredictSuccessRequest,
    PredictTimeRequest,
    SegmentUserRequest,
)

logger = structlog.get_logger()


def _require_loaded(model: LoadedModel) -> LoadedModel:
    if not model.loaded or model.artifact is None:
        raise MLModelUnavailableError(model.name)
    return model


def _row_df(features: dict[str, Any], order: list[str]) -> pd.DataFrame:
    try:
        return pd.DataFrame([{k: features[k] for k in order}])
    except KeyError as exc:
        raise MLInferenceError(f"Falta la característica requerida por el modelo: {exc}") from exc


# ============================================
# Registro de inferencias (SQLite local, no toca la BD de la app)
# ============================================
def _log_inference_sync(model_name: str, model_version: str | None, endpoint: str,
                         input_data: dict, output_data: dict, confidence: float | None) -> None:
    db_path = Path(settings.ML_WAREHOUSE_DB)
    if not db_path.exists():
        # El warehouse se construye con database/warehouse/build_warehouse.py;
        # si aún no existe, no se bloquea la respuesta al usuario por esto.
        logger.warning("ml_inference_log_skipped_no_warehouse", path=str(db_path))
        return
    try:
        con = sqlite3.connect(db_path)
        con.execute(
            """
            INSERT INTO fact_ml_inferences
                (model_name, model_version, endpoint, input_json, output_json, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                model_name, model_version, endpoint,
                json.dumps(input_data, default=str), json.dumps(output_data, default=str),
                confidence, datetime.now(timezone.utc).isoformat(),
            ),
        )
        con.commit()
        con.close()
    except Exception as exc:  # noqa: BLE001
        logger.warning("ml_inference_log_failed", error=str(exc))


async def log_inference(model_name: str, model_version: str | None, endpoint: str,
                         input_data: dict, output_data: dict, confidence: float | None = None) -> None:
    await run_in_threadpool(
        _log_inference_sync, model_name, model_version, endpoint, input_data, output_data, confidence
    )


def get_recent_inferences(limit: int = 50) -> list[dict]:
    db_path = Path(settings.ML_WAREHOUSE_DB)
    if not db_path.exists():
        return []
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT id, model_name, model_version, endpoint, confidence, created_at "
        "FROM fact_ml_inferences ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


# ============================================
# S02 - Tiempo de respuesta
# ============================================
async def predict_time(req: PredictTimeRequest) -> dict:
    model = _require_loaded(get_registry().get("time_estimator"))
    meta = model.metadata or {}
    features = meta.get("features", list(req.model_dump().keys()))
    df = _row_df(req.model_dump(), features)
    try:
        pipeline = model.artifact["pipeline"]
        pred_log = pipeline.predict(df)[0]
        predicted_seconds = float(np.expm1(pred_log)) if meta.get("target_transform") == "log1p" else float(pred_log)
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo predecir el tiempo de respuesta: {exc}") from exc

    result = {
        "predicted_time_seconds": round(max(predicted_seconds, 0.0), 1),
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(model.name, meta.get("version"), "predict-time", req.model_dump(), result)
    return result


# ============================================
# S06 - Éxito conservando vidas
# ============================================
async def predict_success(req: PredictSuccessRequest) -> dict:
    model = _require_loaded(get_registry().get("success_classifier"))
    meta = model.metadata or {}
    features = meta.get("features", list(req.model_dump().keys()))
    df = _row_df(req.model_dump(), features)
    try:
        pipeline = model.artifact["pipeline"]
        pred = bool(pipeline.predict(df)[0])
        proba = pipeline.predict_proba(df)[0]
        classes = list(pipeline.classes_)
        confidence = float(proba[classes.index(True)]) if True in classes else float(max(proba))
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo predecir el éxito del reto: {exc}") from exc

    result = {
        "completed_with_lives": pred,
        "probability": round(confidence, 4),
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(model.name, meta.get("version"), "predict-success", req.model_dump(), result, confidence)
    return result


# ============================================
# U04 - Detección de anomalías
# ============================================
async def detect_anomaly(req: DetectAnomalyRequest) -> dict:
    model = _require_loaded(get_registry().get("anomaly_detector"))
    meta = model.metadata or {}
    features = meta.get("features", list(req.model_dump().keys()))
    df = _row_df(req.model_dump(), features)
    try:
        pipeline = model.artifact["pipeline"]
        label = pipeline.predict(df)[0]  # 1 = normal, -1 = anómalo (IsolationForest/OneClassSVM)
        is_anomaly = bool(label == -1)
        if hasattr(pipeline, "decision_function"):
            score = float(-pipeline.decision_function(df)[0])  # invertido: mayor = más anómalo
        elif hasattr(pipeline, "score_samples"):
            score = float(-pipeline.score_samples(df)[0])
        else:
            score = 1.0 if is_anomaly else 0.0
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo evaluar la anomalía: {exc}") from exc

    result = {
        "is_anomaly": is_anomaly,
        "anomaly_score": round(score, 4),
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(model.name, meta.get("version"), "detect-anomaly", req.model_dump(), result, score)
    return result


# ============================================
# U07 - Segmentación RFM
# ============================================
async def segment_user(req: SegmentUserRequest) -> dict:
    model = _require_loaded(get_registry().get("rfm_kmeans"))
    meta = model.metadata or {}
    features = meta.get("features", list(req.model_dump().keys()))
    df = _row_df(req.model_dump(), features)
    try:
        pipeline = model.artifact["pipeline"]
        cluster = int(pipeline.predict(df)[0])
        scaler = pipeline.named_steps.get("scaler")
        kmeans = pipeline.named_steps.get("kmeans")
        if scaler is not None and kmeans is not None:
            scaled_point = scaler.transform(df)[0]
            centroid = kmeans.cluster_centers_[cluster]
            distance = float(((scaled_point - centroid) ** 2).sum() ** 0.5)
        else:
            distance = 0.0
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo segmentar al usuario: {exc}") from exc

    profiles = meta.get("cluster_profiles", {})
    label = profiles.get(str(cluster), f"Cluster {cluster}")

    result = {
        "cluster": cluster,
        "segment_label": label,
        "distance_to_centroid": round(distance, 4),
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(model.name, meta.get("version"), "segment-user", req.model_dump(), result)
    return result


# ============================================
# S08 - Pronóstico de carga de plataforma
# ============================================
async def forecast_platform_load(horizon_hours: int = 6) -> dict:
    model = _require_loaded(get_registry().get("platform_load_forecaster"))
    meta = model.metadata or {}
    features = meta.get("features", [])

    recent = _recent_platform_load_rows(limit=200)
    if recent.empty:
        raise MLInferenceError("No hay datos recientes de carga de plataforma para pronosticar")

    try:
        pipeline = model.artifact["pipeline"]
        history = recent["requests_per_minute"].tolist()
        last_row = recent.iloc[-1]
        forecast_points = []
        for h in range(1, horizon_hours + 1):
            next_ts = pd.to_datetime(last_row["timestamp"]) + pd.Timedelta(hours=h)
            row = {
                "hour_of_day": int(next_ts.hour),
                "day_of_week": int(next_ts.dayofweek),
                "active_users": float(last_row["active_users"]),
                "db_connections": float(last_row["db_connections"]),
                "avg_response_ms": float(last_row["avg_response_ms"]),
                "requests_lag_1h": float(history[-1]),
                "requests_lag_24h": float(history[-24]) if len(history) >= 24 else float(history[0]),
                "requests_lag_168h": float(history[-168]) if len(history) >= 168 else float(history[0]),
                "requests_rolling_mean_24h": float(pd.Series(history[-24:]).mean()),
                "requests_rolling_std_24h": float(pd.Series(history[-24:]).std() or 0.0),
            }
            df = _row_df(row, features)
            pred = float(pipeline.predict(df)[0])
            history.append(pred)
            forecast_points.append(
                PlatformLoadForecastPoint(horizon_hours=h, predicted_requests_per_minute=round(pred, 1))
            )
    except MLInferenceError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo pronosticar la carga de la plataforma: {exc}") from exc

    result = {
        "forecast": forecast_points,
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(
        model.name, meta.get("version"), "platform-load-forecast",
        {"horizon_hours": horizon_hours}, {"forecast": [p.model_dump() for p in forecast_points]},
    )
    return result


def _recent_platform_load_rows(limit: int = 200) -> pd.DataFrame:
    db_path = Path(settings.ML_WAREHOUSE_DB)
    if not db_path.exists():
        return pd.DataFrame()
    con = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(
            "SELECT * FROM fact_platform_load ORDER BY timestamp DESC LIMIT ?", con, params=(limit,)
        )
    except Exception:  # noqa: BLE001
        df = pd.DataFrame()
    finally:
        con.close()
    return df.iloc[::-1].reset_index(drop=True) if not df.empty else df


# ============================================
# U08 - Análisis de navegación (Markov)
# ============================================
async def analyze_navigation(req: AnalyzeNavigationRequest) -> dict:
    model = _require_loaded(get_registry().get("navigation_markov"))
    artifact = model.artifact or {}
    meta = model.metadata or {}
    try:
        matrix = artifact["transition_matrix"]
        if not isinstance(matrix, pd.DataFrame):
            matrix = pd.DataFrame(matrix)
        row = matrix.loc[req.current_state]
        top = row.sort_values(ascending=False).head(3)
        next_pages = [
            NextPageProbability(page=str(page), probability=round(float(prob), 4))
            for page, prob in top.items()
        ]
        drop_off_risk = round(float(row.get("salir", 0.0)), 4)
    except Exception as exc:  # noqa: BLE001
        raise MLInferenceError(f"No se pudo analizar la navegación: {exc}") from exc

    result = {
        "current_state": req.current_state,
        "next_page_probabilities": next_pages,
        "drop_off_risk": drop_off_risk,
        "model": model.name,
        "model_version": meta.get("version", "unknown"),
        "inference_date": datetime.now(timezone.utc),
    }
    await log_inference(
        model.name, meta.get("version"), "analyze-navigation",
        req.model_dump(), {"drop_off_risk": drop_off_risk, "next_pages": [p.page for p in next_pages]},
    )
    return result
