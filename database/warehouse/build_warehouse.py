"""
Tutunaku - Proceso ETL y construcción del Data Mart analítico (Etapas 6-9).

Extrae los CSV generados por `simulation/generate_dataset.py`, los limpia y
transforma, construye un esquema en estrella en un SQLite LOCAL e independiente
(`database/warehouse/tutunaku_dw.sqlite`) y genera los conjuntos de
entrenamiento/validación/prueba/inferencia en `data/`.

Este proceso NUNCA toca la base de datos MySQL/MongoDB real de la aplicación:
solo lee datos simulados y escribe en su propio almacén analítico, por lo que
no existe riesgo de romper la funcionalidad actual.

Ejecutar:
    python database/warehouse/build_warehouse.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
TRAIN_DIR = ROOT / "data" / "training"
VAL_DIR = ROOT / "data" / "validation"
TEST_DIR = ROOT / "data" / "test"
INFERENCE_DIR = ROOT / "data" / "inference"
WAREHOUSE_DB = Path(__file__).resolve().parent / "tutunaku_dw.sqlite"

for d in (PROCESSED_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR, INFERENCE_DIR):
    d.mkdir(parents=True, exist_ok=True)

quality_report: dict = {"extraction": {}, "transformation": {}, "validation": {}}


def log(section: str, key: str, value) -> None:
    quality_report.setdefault(section, {})[key] = value
    print(f"[{section}] {key}: {value}")


# ---------------------------------------------------------------------------
# EXTRACCIÓN
# ---------------------------------------------------------------------------
def extract() -> dict[str, pd.DataFrame]:
    tables = {}
    for name in ["users", "exercises", "exercise_attempts", "challenge_attempts",
                 "platform_load", "xp_events", "navigation_events"]:
        path = RAW_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"No se encontró {path}. Ejecuta primero simulation/generate_dataset.py"
            )
        df = pd.read_csv(path)
        tables[name] = df
        log("extraction", name, {"filas": len(df), "columnas": list(df.columns)})
    return tables


# ---------------------------------------------------------------------------
# TRANSFORMACIÓN
# ---------------------------------------------------------------------------
def transform_exercise_attempts(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["user_id", "exercise_id", "timestamp", "attempt_number"]).copy()
    log("transformation", "exercise_attempts_duplicados_eliminados", before - len(df))

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    null_connectivity = df["connectivity_quality"].isna().sum()
    df["connectivity_quality"] = df["connectivity_quality"].fillna(df["connectivity_quality"].median())
    log("transformation", "exercise_attempts_conectividad_imputada", int(null_connectivity))

    # No se eliminan outliers (regla: no editar/borrar sin justificar); se marcan.
    p99_5 = df["time_spent_seconds"].quantile(0.995)
    df["time_spent_outlier_flag"] = df["time_spent_seconds"] > p99_5
    log("transformation", "exercise_attempts_outliers_marcados", int(df["time_spent_outlier_flag"].sum()))

    df["log1p_time_spent_seconds"] = np.log1p(df["time_spent_seconds"])
    df["is_correct"] = df["is_correct"].astype(bool)
    return df


def transform_challenge_attempts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["completed_with_lives"] = df["completed_with_lives"].astype(bool)
    return df


def transform_platform_load(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    null_before = df[["requests_per_minute", "db_connections", "avg_response_ms"]].isna().sum().sum()
    for col in ["requests_per_minute", "db_connections", "avg_response_ms"]:
        df[col] = df[col].interpolate(method="linear", limit_direction="both")
    log("transformation", "platform_load_huecos_interpolados", int(null_before))

    # variables de rezago para el pronóstico (Etapa 10, series de tiempo)
    for lag in (1, 24, 168):
        df[f"requests_lag_{lag}h"] = df["requests_per_minute"].shift(lag)
    df["requests_rolling_mean_24h"] = df["requests_per_minute"].rolling(24, min_periods=1).mean()
    df["requests_rolling_std_24h"] = df["requests_per_minute"].rolling(24, min_periods=1).std().fillna(0)
    return df


def transform_xp_events(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    # tiempo desde el evento anterior del mismo usuario (útil para detectar ráfagas)
    df["seconds_since_prev_event"] = (
        df.groupby("user_id")["timestamp"].diff().dt.total_seconds()
    )
    df["seconds_since_prev_event"] = df["seconds_since_prev_event"].fillna(9999)

    # eventos del mismo usuario en la última hora (ritmo de actividad)
    counts = []
    for _, g in df.groupby("user_id"):
        ts = g["timestamp"].values.astype("datetime64[s]").astype(np.int64)
        c = np.array([np.sum((ts >= t - 3600) & (ts <= t)) for t in ts])
        counts.append(pd.Series(c, index=g.index))
    df["events_last_hour_user"] = pd.concat(counts).sort_index()

    df["is_anomaly_injected"] = df["is_anomaly_injected"].astype(bool)
    return df


def transform_navigation_events(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def build_rfm(xp_events: pd.DataFrame, navigation_events: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    """Recencia / Frecuencia / Valor educativo por usuario (Etapa 5.4 y U07)."""
    ref_date = xp_events["timestamp"].max()

    recency = (
        xp_events.groupby("user_id")["timestamp"].max()
        .rename("last_activity")
        .to_frame()
    )
    recency["recency_days"] = (ref_date - recency["last_activity"]).dt.days

    frequency = navigation_events.groupby("user_id")["session_id"].nunique().rename("frequency_sessions")
    monetary = xp_events.groupby("user_id")["xp_gained"].sum().rename("educational_value_xp")

    rfm = users[["user_id", "engagement_segment", "region", "device_type"]].set_index("user_id")
    rfm = rfm.join(recency["recency_days"]).join(frequency).join(monetary)
    rfm[["recency_days", "frequency_sessions", "educational_value_xp"]] = (
        rfm[["recency_days", "frequency_sessions", "educational_value_xp"]].fillna(0)
    )
    return rfm.reset_index()


# ---------------------------------------------------------------------------
# CARGA: esquema en estrella en SQLite
# ---------------------------------------------------------------------------
def load_warehouse(tables: dict[str, pd.DataFrame], rfm: pd.DataFrame) -> None:
    if WAREHOUSE_DB.exists():
        WAREHOUSE_DB.unlink()
    con = sqlite3.connect(WAREHOUSE_DB)
    try:
        tables["users"].to_sql("dim_user", con, index=False)
        tables["exercises"].to_sql("dim_exercise", con, index=False)
        tables["exercise_attempts"].to_sql("fact_exercise_attempts", con, index=False)
        tables["challenge_attempts"].to_sql("fact_challenge_attempts", con, index=False)
        tables["platform_load"].to_sql("fact_platform_load", con, index=False)
        tables["xp_events"].to_sql("fact_xp_events", con, index=False)
        tables["navigation_events"].to_sql("fact_navigation_events", con, index=False)
        rfm.to_sql("dim_user_rfm", con, index=False)
        # Tabla vacía que el backend poblará con cada inferencia real del API /api/ml
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS fact_ml_inferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_version TEXT,
                endpoint TEXT NOT NULL,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL,
                confidence REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        con.commit()
    finally:
        con.close()
    log("transformation", "warehouse_sqlite", str(WAREHOUSE_DB))


# ---------------------------------------------------------------------------
# VALIDACIÓN
# ---------------------------------------------------------------------------
def validate(tables: dict[str, pd.DataFrame]) -> None:
    for name, df in tables.items():
        log("validation", f"{name}_filas", len(df))
        log("validation", f"{name}_nulos_totales", int(df.isna().sum().sum()))
    assert tables["exercise_attempts"]["time_spent_seconds"].min() > 0, "tiempo de respuesta no puede ser <= 0"
    assert tables["platform_load"]["requests_per_minute"].isna().sum() == 0, "quedaron huecos sin interpolar"


# ---------------------------------------------------------------------------
# SPLITS 70/15/15 (Etapa 9) — reproducibles con semilla 2026
# ---------------------------------------------------------------------------
def split_row_level(df: pd.DataFrame, name: str, stratify_col: str | None = None) -> None:
    rng = np.random.default_rng(SEED)
    n = len(df)
    idx = rng.permutation(n)
    if stratify_col is not None:
        # split estratificado simple por clase para preservar el balance
        parts_train, parts_val, parts_test = [], [], []
        for _, group in df.groupby(stratify_col):
            gi = rng.permutation(len(group))
            g = group.iloc[gi]
            n_train = int(len(g) * 0.70)
            n_val = int(len(g) * 0.15)
            parts_train.append(g.iloc[:n_train])
            parts_val.append(g.iloc[n_train:n_train + n_val])
            parts_test.append(g.iloc[n_train + n_val:])
        train = pd.concat(parts_train).sample(frac=1, random_state=SEED).reset_index(drop=True)
        val = pd.concat(parts_val).sample(frac=1, random_state=SEED).reset_index(drop=True)
        test = pd.concat(parts_test).sample(frac=1, random_state=SEED).reset_index(drop=True)
    else:
        df_shuffled = df.iloc[idx].reset_index(drop=True)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        train = df_shuffled.iloc[:n_train]
        val = df_shuffled.iloc[n_train:n_train + n_val]
        test = df_shuffled.iloc[n_train + n_val:]

    train.to_csv(TRAIN_DIR / f"{name}_train.csv", index=False)
    val.to_csv(VAL_DIR / f"{name}_validation.csv", index=False)
    test.to_csv(TEST_DIR / f"{name}_test.csv", index=False)
    test.sample(n=min(20, len(test)), random_state=SEED).to_csv(INFERENCE_DIR / f"{name}_inference_sample.csv", index=False)
    log("validation", f"{name}_split", {"train": len(train), "validation": len(val), "test": len(test)})


def split_time_series(df: pd.DataFrame, name: str) -> None:
    df = df.sort_values("timestamp").reset_index(drop=True)
    n = len(df)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    train = df.iloc[:n_train]
    val = df.iloc[n_train:n_train + n_val]
    test = df.iloc[n_train + n_val:]

    train.to_csv(TRAIN_DIR / f"{name}_train.csv", index=False)
    val.to_csv(VAL_DIR / f"{name}_validation.csv", index=False)
    test.to_csv(TEST_DIR / f"{name}_test.csv", index=False)
    test.tail(20).to_csv(INFERENCE_DIR / f"{name}_inference_sample.csv", index=False)
    log("validation", f"{name}_split_temporal", {
        "train": f"{train['timestamp'].min()} -> {train['timestamp'].max()}",
        "validation": f"{val['timestamp'].min()} -> {val['timestamp'].max()}",
        "test": f"{test['timestamp'].min()} -> {test['timestamp'].max()}",
    })


def main() -> None:
    raw = extract()

    exercise_attempts = transform_exercise_attempts(raw["exercise_attempts"])
    challenge_attempts = transform_challenge_attempts(raw["challenge_attempts"])
    platform_load = transform_platform_load(raw["platform_load"])
    xp_events = transform_xp_events(raw["xp_events"])
    navigation_events = transform_navigation_events(raw["navigation_events"])
    rfm = build_rfm(xp_events, navigation_events, raw["users"])

    processed = {
        "users": raw["users"],
        "exercises": raw["exercises"],
        "exercise_attempts": exercise_attempts,
        "challenge_attempts": challenge_attempts,
        "platform_load": platform_load,
        "xp_events": xp_events,
        "navigation_events": navigation_events,
    }
    for name, df in processed.items():
        df.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    rfm.to_csv(PROCESSED_DIR / "user_rfm.csv", index=False)

    validate(processed)
    load_warehouse(processed, rfm)

    split_row_level(exercise_attempts, "exercise_attempts")
    split_row_level(challenge_attempts, "challenge_attempts", stratify_col="completed_with_lives")
    split_time_series(platform_load, "platform_load")

    report_path = PROCESSED_DIR / "etl_quality_report.json"
    report_path.write_text(json.dumps(quality_report, indent=2, default=str), encoding="utf-8")
    print(f"\nReporte de calidad ETL: {report_path}")
    print(f"Data Warehouse: {WAREHOUSE_DB}")


if __name__ == "__main__":
    main()
