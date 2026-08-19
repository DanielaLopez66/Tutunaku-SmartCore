"""
Tutunaku - Pruebas de la API Inteligente (/api/ml)

A diferencia de test_auth.py (prueba de integración que requiere MySQL/MongoDB
reales), estas pruebas NO dependen de ninguna base de datos transaccional: los
endpoints de /api/ml solo leen los modelos serializados (models/serialized/) y
el Data Warehouse analítico local (database/warehouse/tutunaku_dw.sqlite), así
que corren de forma aislada y reproducible en cualquier entorno.
"""
import pytest

from app.core.security import create_access_token

VALID_TIME_PAYLOAD = {
    "attempt_number": 1,
    "difficulty": 3,
    "connectivity_quality": 0.8,
    "device_type": "mobile",
    "hour_of_day": 14,
    "day_of_week": 2,
    "is_correct": True,
    "hearts_before": 5,
}

VALID_SUCCESS_PAYLOAD = {
    "difficulty": 3,
    "num_exercises": 10,
    "connectivity_quality": 0.8,
    "device_type": "desktop",
    "prior_success_rate_30d": 0.7,
    "hearts_start": 5,
}

VALID_ANOMALY_PAYLOAD = {
    "xp_gained": 15,
    "session_duration_seconds": 30,
    "seconds_since_prev_event": 120,
    "events_last_hour_user": 3,
}

VALID_SEGMENT_PAYLOAD = {
    "recency_days": 2,
    "frequency_sessions": 12,
    "educational_value_xp": 2500,
}


def _token(role: str = "user") -> str:
    return create_access_token(subject="test-user-id", role=role)


def _auth(role: str = "user") -> dict:
    return {"Authorization": f"Bearer {_token(role)}"}


@pytest.mark.asyncio
async def test_ml_health_no_auth_required(client):
    resp = await client.get("/api/ml/health")
    assert resp.status_code == 200
    body = resp.json()
    assert "models" in body
    assert set(body["models"]) == {
        "time_estimator", "success_classifier", "platform_load_forecaster",
        "anomaly_detector", "navigation_markov", "rfm_kmeans",
    }


@pytest.mark.asyncio
async def test_ml_models_requires_auth(client):
    resp = await client.get("/api/ml/models")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ml_models_lists_catalog(client):
    resp = await client.get("/api/ml/models", headers=_auth("user"))
    assert resp.status_code == 200
    models = resp.json()
    assert len(models) == 6
    assert all("metrics" in m and "version" in m for m in models)


@pytest.mark.asyncio
async def test_predict_time_requires_auth(client):
    resp = await client.post("/api/ml/predict-time", json=VALID_TIME_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_predict_time_valid_payload(client):
    resp = await client.post("/api/ml/predict-time", json=VALID_TIME_PAYLOAD, headers=_auth("user"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["predicted_time_seconds"] > 0
    assert body["model"] == "time_estimator"


@pytest.mark.asyncio
async def test_predict_time_invalid_payload(client):
    bad_payload = {**VALID_TIME_PAYLOAD, "difficulty": 99, "device_type": "smartwatch"}
    resp = await client.post("/api/ml/predict-time", json=bad_payload, headers=_auth("user"))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_time_missing_field(client):
    incomplete = {k: v for k, v in VALID_TIME_PAYLOAD.items() if k != "difficulty"}
    resp = await client.post("/api/ml/predict-time", json=incomplete, headers=_auth("user"))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_success_valid_payload(client):
    resp = await client.post("/api/ml/predict-success", json=VALID_SUCCESS_PAYLOAD, headers=_auth("user"))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["completed_with_lives"], bool)
    assert 0.0 <= body["probability"] <= 1.0


@pytest.mark.asyncio
async def test_detect_anomaly_requires_admin(client):
    resp = await client.post("/api/ml/detect-anomaly", json=VALID_ANOMALY_PAYLOAD, headers=_auth("user"))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_detect_anomaly_as_admin(client):
    resp = await client.post("/api/ml/detect-anomaly", json=VALID_ANOMALY_PAYLOAD, headers=_auth("admin"))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["is_anomaly"], bool)


@pytest.mark.asyncio
async def test_detect_anomaly_negative_value_rejected(client):
    bad_payload = {**VALID_ANOMALY_PAYLOAD, "xp_gained": -5}
    resp = await client.post("/api/ml/detect-anomaly", json=bad_payload, headers=_auth("admin"))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_segment_user_as_admin(client):
    resp = await client.post("/api/ml/segment-user", json=VALID_SEGMENT_PAYLOAD, headers=_auth("admin"))
    assert resp.status_code == 200
    body = resp.json()
    assert "cluster" in body and "segment_label" in body


@pytest.mark.asyncio
async def test_platform_load_forecast_as_admin(client):
    resp = await client.get("/api/ml/platform-load-forecast?horizon_hours=3", headers=_auth("admin"))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["forecast"]) == 3


@pytest.mark.asyncio
async def test_analyze_navigation_as_admin(client):
    resp = await client.post(
        "/api/ml/analyze-navigation", json={"current_state": "leccion"}, headers=_auth("admin")
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["next_page_probabilities"]) == 3


@pytest.mark.asyncio
async def test_analyze_navigation_invalid_state_rejected(client):
    resp = await client.post(
        "/api/ml/analyze-navigation", json={"current_state": "estado_inexistente"}, headers=_auth("admin")
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_trigger_platform_load_update_requires_admin(client):
    resp = await client.post("/api/ml/trigger/platform-load-update", headers=_auth("user"))
    assert resp.status_code == 403

    resp_admin = await client.post("/api/ml/trigger/platform-load-update", headers=_auth("admin"))
    assert resp_admin.status_code == 200
    assert resp_admin.json()["event"] == "platform_load_update"


@pytest.mark.asyncio
async def test_trigger_user_progress_update_requires_admin(client):
    resp = await client.post("/api/ml/trigger/user-progress-update", headers=_auth("user"))
    assert resp.status_code == 403

    resp_admin = await client.post("/api/ml/trigger/user-progress-update", headers=_auth("admin"))
    assert resp_admin.status_code == 200
    assert resp_admin.json()["event"] == "user_progress_update"


@pytest.mark.asyncio
async def test_inferences_history_requires_admin(client):
    resp = await client.get("/api/ml/inferences", headers=_auth("user"))
    assert resp.status_code == 403

    resp_admin = await client.get("/api/ml/inferences", headers=_auth("admin"))
    assert resp_admin.status_code == 200
    assert isinstance(resp_admin.json(), list)
