"""
Tutunaku - Pruebas del proceso ETL (Etapa 16.3 de la guía).

Combina pruebas unitarias de las transformaciones (con DataFrames pequeños y
controlados) con pruebas de integridad sobre los artefactos ya generados por
`database/warehouse/build_warehouse.py` (Data Warehouse SQLite y splits).
"""
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database.warehouse import build_warehouse as etl  # noqa: E402


# ---------------------------------------------------------------------------
# Unitarias: transformaciones sobre datos sintéticos pequeños
# ---------------------------------------------------------------------------
def test_transform_exercise_attempts_deduplicates_and_imputes():
    df = pd.DataFrame({
        "attempt_id": [1, 2, 3, 4],
        "user_id": [1, 1, 1, 1],
        "exercise_id": [10, 10, 11, 11],
        "timestamp": ["2026-01-01T10:00:00"] * 2 + ["2026-01-01T11:00:00"] * 2,
        "attempt_number": [1, 1, 1, 1],
        "difficulty": [3, 3, 2, 2],
        "connectivity_quality": [0.8, 0.8, np.nan, np.nan],
        "device_type": ["mobile"] * 4,
        "hearts_before": [5, 5, 5, 5],
        "is_correct": [True, True, False, False],
        "time_spent_seconds": [20.0, 20.0, 15.0, 15.0],
    })
    out = etl.transform_exercise_attempts(df)
    # las filas 1-2 son duplicadas (mismo user/exercise/timestamp/attempt_number) -> se colapsan
    assert len(out) == 2
    # la conectividad nula se imputa con la mediana, no queda NaN
    assert out["connectivity_quality"].isna().sum() == 0
    assert "log1p_time_spent_seconds" in out.columns
    assert np.isclose(out.loc[out["time_spent_seconds"] == 20.0, "log1p_time_spent_seconds"].iloc[0], np.log1p(20.0))


def test_transform_platform_load_interpolates_gaps_and_adds_lags():
    hours = pd.date_range("2026-01-01", periods=200, freq="h")
    values = np.linspace(100, 300, len(hours))
    values[50] = np.nan  # hueco de monitoreo simulado
    df = pd.DataFrame({
        "timestamp": hours,
        "hour_of_day": hours.hour,
        "day_of_week": hours.dayofweek,
        "active_users": 100,
        "requests_per_minute": values,
        "db_connections": 10.0,
        "avg_response_ms": 120.0,
    })
    out = etl.transform_platform_load(df)
    assert out["requests_per_minute"].isna().sum() == 0  # el hueco se interpoló
    for col in ("requests_lag_1h", "requests_lag_24h", "requests_lag_168h",
                "requests_rolling_mean_24h", "requests_rolling_std_24h"):
        assert col in out.columns


def test_split_row_level_respects_70_15_15(tmp_path, monkeypatch):
    monkeypatch.setattr(etl, "TRAIN_DIR", tmp_path / "train")
    monkeypatch.setattr(etl, "VAL_DIR", tmp_path / "val")
    monkeypatch.setattr(etl, "TEST_DIR", tmp_path / "test")
    monkeypatch.setattr(etl, "INFERENCE_DIR", tmp_path / "inference")
    for d in (etl.TRAIN_DIR, etl.VAL_DIR, etl.TEST_DIR, etl.INFERENCE_DIR):
        d.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({"id": range(1000), "value": np.random.default_rng(1).random(1000)})
    etl.split_row_level(df, "dummy")

    train = pd.read_csv(etl.TRAIN_DIR / "dummy_train.csv")
    val = pd.read_csv(etl.VAL_DIR / "dummy_validation.csv")
    test = pd.read_csv(etl.TEST_DIR / "dummy_test.csv")

    assert len(train) + len(val) + len(test) == 1000
    assert abs(len(train) - 700) <= 2
    assert abs(len(val) - 150) <= 2
    # sin fuga de información: ningún id se repite entre conjuntos
    assert set(train["id"]) & set(val["id"]) == set()
    assert set(train["id"]) & set(test["id"]) == set()
    assert set(val["id"]) & set(test["id"]) == set()


# ---------------------------------------------------------------------------
# Integridad: artefactos ya generados por el pipeline real (data/, warehouse)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not etl.WAREHOUSE_DB.exists(), reason="Ejecuta primero database/warehouse/build_warehouse.py")
def test_warehouse_sqlite_has_expected_tables():
    con = sqlite3.connect(etl.WAREHOUSE_DB)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    expected = {
        "dim_user", "dim_exercise", "fact_exercise_attempts", "fact_challenge_attempts",
        "fact_platform_load", "fact_xp_events", "fact_navigation_events",
        "dim_user_rfm", "fact_ml_inferences",
    }
    assert expected.issubset(tables)


@pytest.mark.skipif(not (etl.PROCESSED_DIR / "etl_quality_report.json").exists(), reason="ETL aún no ejecutado")
def test_processed_exercise_attempts_no_negative_times():
    df = pd.read_csv(etl.PROCESSED_DIR / "exercise_attempts.csv")
    assert (df["time_spent_seconds"] > 0).all()
    assert df["connectivity_quality"].isna().sum() == 0
