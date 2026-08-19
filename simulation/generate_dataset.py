"""
Tutunaku - Simulador estratégico de datasets (Etapa 5 de la guía).

Genera datos SINTÉTICOS y reproducibles (semilla fija) para alimentar los 6
escenarios de Machine Learning del proyecto. No se conecta a la base de datos
real de la aplicación: esto evita cualquier riesgo sobre la app en producción.

Reglas de simulación (no aleatoriedad total):
- Cada usuario tiene rasgos latentes (segmento de compromiso, calidad de
  conectividad base, dispositivo) que influyen de forma consistente en el
  resto de las tablas (más sesiones, más XP, tiempos de respuesta distintos).
- La carga de la plataforma tiene estacionalidad diaria/semanal y una
  tendencia de crecimiento, más eventos especiales (picos).
- Se inyectan explícitamente casos extremos, faltantes y anómalos, documentados
  con una bandera `is_anomaly_injected` (NO se usa como feature de entrenamiento,
  solo sirve para validar los modelos no supervisados).

Ejecutar:
    python simulation/generate_dataset.py
Salida:
    data/raw/*.csv
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

N_USERS = 800
N_EXERCISES = 120
N_DAYS = 120
START_DATE = dt.date(2026, 1, 1)

EXERCISE_TYPES = ["translation", "multiple_choice", "writing", "audio"]
REGIONS = ["urbano", "semiurbano", "rural"]
DEVICES = ["mobile", "desktop", "tablet"]
ENGAGEMENT_SEGMENTS = ["casual", "regular", "dedicado"]
NAV_STATES = [
    "home", "mapa_niveles", "leccion", "ejercicio", "resultado",
    "logros", "leaderboard", "perfil", "configuracion", "salir",
]


def _rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


# ---------------------------------------------------------------------------
# 1. Usuarios (dimensión compartida por todos los escenarios)
# ---------------------------------------------------------------------------
def generate_users(rng: np.random.Generator, n_users: int = N_USERS) -> pd.DataFrame:
    engagement = rng.choice(ENGAGEMENT_SEGMENTS, size=n_users, p=[0.5, 0.35, 0.15])
    # El compromiso influye en la antigüedad (usuarios dedicados llevan más tiempo)
    tenure_days = np.where(
        engagement == "dedicado", rng.integers(60, N_DAYS, n_users),
        np.where(engagement == "regular", rng.integers(20, N_DAYS, n_users),
                 rng.integers(1, N_DAYS, n_users)),
    )
    signup_date = [START_DATE + dt.timedelta(days=int(N_DAYS - t)) for t in tenure_days]

    region = rng.choice(REGIONS, size=n_users, p=[0.55, 0.30, 0.15])
    device = rng.choice(DEVICES, size=n_users, p=[0.65, 0.25, 0.10])

    # La conectividad base depende de la región (regla de negocio, no azar puro)
    base_connectivity = np.select(
        [region == "urbano", region == "semiurbano", region == "rural"],
        [rng.normal(0.88, 0.07, n_users), rng.normal(0.72, 0.10, n_users), rng.normal(0.52, 0.14, n_users)],
    )
    base_connectivity = np.clip(base_connectivity, 0.05, 1.0)

    df = pd.DataFrame({
        "user_id": np.arange(1, n_users + 1),
        "signup_date": signup_date,
        "region": region,
        "device_type": device,
        "engagement_segment": engagement,
        "base_connectivity_score": base_connectivity.round(3),
    })
    return df


# ---------------------------------------------------------------------------
# 2. Ejercicios
# ---------------------------------------------------------------------------
def generate_exercises(rng: np.random.Generator, n_exercises: int = N_EXERCISES) -> pd.DataFrame:
    difficulty = rng.integers(1, 6, n_exercises)  # 1..5
    ex_type = rng.choice(EXERCISE_TYPES, size=n_exercises, p=[0.3, 0.35, 0.2, 0.15])
    # Los ejercicios de escritura/audio toman más tiempo base que opción múltiple
    base_time = np.select(
        [ex_type == "multiple_choice", ex_type == "translation", ex_type == "audio", ex_type == "writing"],
        [8 + difficulty * 1.5, 12 + difficulty * 2.0, 15 + difficulty * 2.2, 20 + difficulty * 3.0],
    )
    df = pd.DataFrame({
        "exercise_id": np.arange(1, n_exercises + 1),
        "type": ex_type,
        "difficulty": difficulty,
        "base_time_seconds": base_time.round(1),
    })
    return df


# ---------------------------------------------------------------------------
# 3. Intentos de ejercicio -> S02 (regresión de tiempo de respuesta)
# ---------------------------------------------------------------------------
def generate_exercise_attempts(rng: np.random.Generator, users: pd.DataFrame, exercises: pd.DataFrame,
                                n_attempts: int = 60_000) -> pd.DataFrame:
    engagement_weight = users["engagement_segment"].map({"dedicado": 3.0, "regular": 1.6, "casual": 0.7}).to_numpy()
    user_probs = engagement_weight / engagement_weight.sum()
    user_idx = rng.choice(users.index.to_numpy(), size=n_attempts, p=user_probs)
    exercise_idx = rng.choice(exercises.index.to_numpy(), size=n_attempts)

    u = users.iloc[user_idx].reset_index(drop=True)
    e = exercises.iloc[exercise_idx].reset_index(drop=True)

    days_offset = rng.integers(0, N_DAYS, n_attempts)
    seconds_offset = rng.integers(0, 86_400, n_attempts)
    timestamp = [
        dt.datetime.combine(START_DATE, dt.time()) + dt.timedelta(days=int(d), seconds=int(s))
        for d, s in zip(days_offset, seconds_offset)
    ]

    attempt_number = rng.geometric(0.6, n_attempts).clip(1, 6)
    connectivity_quality = np.clip(u["base_connectivity_score"].to_numpy() + rng.normal(0, 0.08, n_attempts), 0.03, 1.0)
    hearts_before = rng.integers(1, 6, n_attempts)

    # tiempo esperado: base del ejercicio + penalización por baja conectividad
    # + penalización por dificultad + ligera mejora por intentos repetidos (familiaridad)
    device_penalty = np.select(
        [u["device_type"] == "mobile", u["device_type"] == "tablet", u["device_type"] == "desktop"],
        [1.15, 1.05, 1.0],
    )
    connectivity_penalty = 1 + (1 - connectivity_quality) * 1.8
    familiarity_bonus = np.clip(1 - (attempt_number - 1) * 0.08, 0.6, 1.0)

    expected_time = (
        e["base_time_seconds"].to_numpy() * device_penalty * connectivity_penalty * familiarity_bonus
    )
    noise = rng.lognormal(mean=0, sigma=0.35, size=n_attempts)
    time_spent = np.clip(expected_time * noise, 2, 600)

    # probabilidad de acierto: baja con dificultad y sube con familiaridad/compromiso
    engagement_bonus = u["engagement_segment"].map({"dedicado": 0.12, "regular": 0.04, "casual": -0.05}).to_numpy()
    correct_logit = (
        1.6 - e["difficulty"].to_numpy() * 0.28 + (attempt_number - 1) * 0.18
        + engagement_bonus + (connectivity_quality - 0.5) * 0.4
    )
    correct_prob = 1 / (1 + np.exp(-correct_logit))
    is_correct = rng.random(n_attempts) < correct_prob

    df = pd.DataFrame({
        "attempt_id": np.arange(1, n_attempts + 1),
        "user_id": u["user_id"].to_numpy(),
        "exercise_id": e["exercise_id"].to_numpy(),
        "timestamp": timestamp,
        "attempt_number": attempt_number,
        "difficulty": e["difficulty"].to_numpy(),
        "connectivity_quality": connectivity_quality.round(3),
        "device_type": u["device_type"].to_numpy(),
        "hearts_before": hearts_before,
        "is_correct": is_correct,
        "time_spent_seconds": time_spent.round(1),
    })

    # --- casos extremos / faltantes / anómalos documentados ---
    n = len(df)
    missing_idx = rng.choice(n, size=int(n * 0.015), replace=False)
    df.loc[missing_idx, "connectivity_quality"] = np.nan  # sensor de red no reportó
    outlier_idx = rng.choice(n, size=int(n * 0.005), replace=False)
    df.loc[outlier_idx, "time_spent_seconds"] = rng.uniform(500, 590, len(outlier_idx))  # usuario distraído / app en pausa
    dup_idx = rng.choice(n, size=int(n * 0.003), replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)  # reintentos de red duplicando el POST

    return df


# ---------------------------------------------------------------------------
# 4. Retos completos -> S06 (clasificación binaria de éxito conservando vidas)
# ---------------------------------------------------------------------------
def generate_challenge_attempts(rng: np.random.Generator, users: pd.DataFrame,
                                 n_challenges: int = 18_000) -> pd.DataFrame:
    engagement_weight = users["engagement_segment"].map({"dedicado": 2.5, "regular": 1.5, "casual": 0.8}).to_numpy()
    user_probs = engagement_weight / engagement_weight.sum()
    user_idx = rng.choice(users.index.to_numpy(), size=n_challenges, p=user_probs)
    u = users.iloc[user_idx].reset_index(drop=True)

    difficulty = rng.integers(1, 6, n_challenges)
    num_exercises = rng.integers(5, 16, n_challenges)
    connectivity_quality = np.clip(u["base_connectivity_score"].to_numpy() + rng.normal(0, 0.08, n_challenges), 0.03, 1.0)
    engagement_bonus = u["engagement_segment"].map({"dedicado": 0.18, "regular": 0.06, "casual": -0.08}).to_numpy()
    prior_success_rate_30d = np.clip(0.55 + engagement_bonus + rng.normal(0, 0.1, n_challenges), 0.05, 0.98)

    hearts_start = np.full(n_challenges, 5)
    fail_logit = (
        difficulty * 0.35 - engagement_bonus * 3 - (connectivity_quality - 0.5) * 1.2
        + (num_exercises - 10) * 0.05 - (prior_success_rate_30d - 0.5) * 1.5
    )
    fail_prob_per_exercise = np.clip(1 / (1 + np.exp(-fail_logit)) * 0.35, 0.02, 0.85)
    hearts_lost = rng.binomial(num_exercises, fail_prob_per_exercise)
    hearts_end = np.clip(hearts_start - hearts_lost, 0, hearts_start)
    completed_with_lives = hearts_end > 0

    df = pd.DataFrame({
        "challenge_id": np.arange(1, n_challenges + 1),
        "user_id": u["user_id"].to_numpy(),
        "difficulty": difficulty,
        "num_exercises": num_exercises,
        "connectivity_quality": connectivity_quality.round(3),
        "device_type": u["device_type"].to_numpy(),
        "prior_success_rate_30d": prior_success_rate_30d.round(3),
        "hearts_start": hearts_start,
        "hearts_end": hearts_end,
        "completed_with_lives": completed_with_lives,
    })
    return df


# ---------------------------------------------------------------------------
# 5. Carga de la plataforma -> S08 (pronóstico de serie temporal)
# ---------------------------------------------------------------------------
def generate_platform_load(rng: np.random.Generator, n_days: int = N_DAYS) -> pd.DataFrame:
    hours = pd.date_range(
        dt.datetime.combine(START_DATE, dt.time()), periods=n_days * 24, freq="h",
    )
    hour_of_day = hours.hour.to_numpy()
    day_of_week = hours.dayofweek.to_numpy()  # 0=lunes
    t = np.arange(len(hours))

    # estacionalidad diaria: picos 18h-22h, valle 3h-6h
    daily = 1 + 0.9 * np.exp(-((hour_of_day - 20) ** 2) / (2 * 3.5 ** 2))
    # estacionalidad semanal: más uso entre semana por la tarde/noche
    weekly = np.where(day_of_week < 5, 1.15, 0.85)
    # tendencia de crecimiento suave (adopción de la plataforma)
    trend = 1 + t / len(t) * 0.6
    base_active_users = 180 * daily * weekly * trend

    noise = rng.normal(1, 0.08, len(hours))
    active_users = np.clip(base_active_users * noise, 5, None)

    # eventos especiales: campañas / lanzamientos de unidades (picos abruptos)
    event_days = rng.choice(n_days, size=max(1, n_days // 20), replace=False)
    for ed in event_days:
        mask = (t >= ed * 24) & (t < ed * 24 + 24)
        active_users[mask] *= rng.uniform(1.4, 2.2)

    requests_per_minute = active_users * rng.normal(2.3, 0.15, len(hours))
    db_connections = np.clip(active_users * rng.normal(0.18, 0.02, len(hours)), 1, None)
    avg_response_ms = 80 + (active_users / active_users.max()) * 260 + rng.normal(0, 12, len(hours))

    df = pd.DataFrame({
        "timestamp": hours,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "active_users": active_users.round(0),
        "requests_per_minute": requests_per_minute.round(1),
        "db_connections": db_connections.round(0),
        "avg_response_ms": np.clip(avg_response_ms, 30, None).round(1),
    })

    # huecos de monitoreo (faltantes reales de logging)
    gap_idx = rng.choice(len(df), size=int(len(df) * 0.01), replace=False)
    df.loc[gap_idx, ["requests_per_minute", "db_connections", "avg_response_ms"]] = np.nan

    return df


# ---------------------------------------------------------------------------
# 6. Eventos de XP -> U04 (detección de anomalías)
# ---------------------------------------------------------------------------
def generate_xp_events(rng: np.random.Generator, users: pd.DataFrame, n_events: int = 40_000) -> pd.DataFrame:
    engagement_weight = users["engagement_segment"].map({"dedicado": 2.8, "regular": 1.4, "casual": 0.6}).to_numpy()
    user_probs = engagement_weight / engagement_weight.sum()
    user_idx = rng.choice(users.index.to_numpy(), size=n_events, p=user_probs)
    u = users.iloc[user_idx].reset_index(drop=True)

    source = rng.choice(
        ["exercise", "lesson_complete", "achievement", "streak_bonus", "daily_bonus"],
        size=n_events, p=[0.55, 0.2, 0.1, 0.1, 0.05],
    )
    base_xp = np.select(
        [source == "exercise", source == "lesson_complete", source == "achievement",
         source == "streak_bonus", source == "daily_bonus"],
        [10, 40, 80, 25, 15],
    )
    xp_gained = np.clip(base_xp * rng.lognormal(0, 0.25, n_events), 1, None).round(0)

    days_offset = rng.integers(0, N_DAYS, n_events)
    seconds_offset = rng.integers(0, 86_400, n_events)
    timestamp = [
        dt.datetime.combine(START_DATE, dt.time()) + dt.timedelta(days=int(d), seconds=int(s))
        for d, s in zip(days_offset, seconds_offset)
    ]
    session_duration_seconds = np.clip(rng.normal(35, 15, n_events), 3, None).round(1)

    df = pd.DataFrame({
        "event_id": np.arange(1, n_events + 1),
        "user_id": u["user_id"].to_numpy(),
        "timestamp": timestamp,
        "source": source,
        "xp_gained": xp_gained,
        "session_duration_seconds": session_duration_seconds,
        "is_anomaly_injected": False,
    })
    df = df.sort_values("timestamp").reset_index(drop=True)

    # --- comportamiento sospechoso inyectado (ground truth solo para validación) ---
    n = len(df)
    # (a) XP imposible: valores muy por encima de cualquier fuente legítima
    xp_anom_idx = rng.choice(n, size=int(n * 0.006), replace=False)
    df.loc[xp_anom_idx, "xp_gained"] = rng.uniform(500, 2000, len(xp_anom_idx)).round(0)
    df.loc[xp_anom_idx, "is_anomaly_injected"] = True

    # (b) automatización: ráfagas de eventos casi idénticos con duración de sesión mínima
    bot_users = rng.choice(users["user_id"].to_numpy(), size=6, replace=False)
    bot_rows = []
    for bu in bot_users:
        burst_start = dt.datetime.combine(START_DATE, dt.time()) + dt.timedelta(
            days=int(rng.integers(0, N_DAYS)), hours=int(rng.integers(0, 24)))
        for k in range(rng.integers(30, 60)):
            bot_rows.append({
                "event_id": -1,
                "user_id": bu,
                "timestamp": burst_start + dt.timedelta(seconds=3 * k),
                "source": "exercise",
                "xp_gained": 10.0,
                "session_duration_seconds": 2.0,
                "is_anomaly_injected": True,
            })
    bot_df = pd.DataFrame(bot_rows)
    bot_df["event_id"] = np.arange(n + 1, n + 1 + len(bot_df))
    df = pd.concat([df, bot_df], ignore_index=True).sort_values("timestamp").reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# 7. Secuencias de navegación -> U08 (cadenas de Markov)
# ---------------------------------------------------------------------------
def _true_transition_matrix(rng: np.random.Generator) -> pd.DataFrame:
    """Matriz de transición 'real' usada para simular navegación coherente."""
    n = len(NAV_STATES)
    idx = {s: i for i, s in enumerate(NAV_STATES)}
    mat = np.full((n, n), 0.01)
    # rutas frecuentes de la app (definidas por el flujo real de producto)
    common_paths = [
        ("home", "mapa_niveles", 0.7), ("home", "leaderboard", 0.15), ("home", "perfil", 0.1),
        ("mapa_niveles", "leccion", 0.85), ("mapa_niveles", "home", 0.1),
        ("leccion", "ejercicio", 0.9),
        ("ejercicio", "ejercicio", 0.55), ("ejercicio", "resultado", 0.35), ("ejercicio", "salir", 0.1),
        ("resultado", "mapa_niveles", 0.55), ("resultado", "logros", 0.15), ("resultado", "salir", 0.3),
        ("logros", "mapa_niveles", 0.5), ("logros", "salir", 0.5),
        ("leaderboard", "home", 0.6), ("leaderboard", "salir", 0.4),
        ("perfil", "configuracion", 0.4), ("perfil", "home", 0.4), ("perfil", "salir", 0.2),
        ("configuracion", "perfil", 0.6), ("configuracion", "salir", 0.4),
        ("salir", "salir", 1.0),
    ]
    for a, b, p in common_paths:
        mat[idx[a], idx[b]] = p
    mat = mat / mat.sum(axis=1, keepdims=True)
    return pd.DataFrame(mat, index=NAV_STATES, columns=NAV_STATES)


def generate_navigation_sequences(rng: np.random.Generator, users: pd.DataFrame,
                                   n_sessions: int = 8000) -> pd.DataFrame:
    trans = _true_transition_matrix(rng)
    engagement_weight = users["engagement_segment"].map({"dedicado": 2.2, "regular": 1.3, "casual": 0.8}).to_numpy()
    user_probs = engagement_weight / engagement_weight.sum()
    session_users = rng.choice(users["user_id"].to_numpy(), size=n_sessions, p=user_probs)

    rows = []
    for session_id, user_id in enumerate(session_users, start=1):
        state = "home"
        t0 = dt.datetime.combine(START_DATE, dt.time()) + dt.timedelta(
            days=int(rng.integers(0, N_DAYS)), seconds=int(rng.integers(0, 86_400)))
        step = 0
        while state != "salir" and step < 25:
            rows.append({
                "session_id": session_id, "user_id": user_id, "step_index": step,
                "page": state, "timestamp": t0 + dt.timedelta(seconds=20 * step),
            })
            probs = trans.loc[state].to_numpy()
            state = rng.choice(NAV_STATES, p=probs)
            step += 1
        rows.append({
            "session_id": session_id, "user_id": user_id, "step_index": step,
            "page": "salir", "timestamp": t0 + dt.timedelta(seconds=20 * step),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
def main() -> None:
    np.random.seed(SEED)  # exigido por la guía (Etapa 5.5), además del Generator con semilla
    rng = _rng()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    users = generate_users(rng)
    exercises = generate_exercises(rng)
    exercise_attempts = generate_exercise_attempts(rng, users, exercises)
    challenge_attempts = generate_challenge_attempts(rng, users)
    platform_load = generate_platform_load(rng)
    xp_events = generate_xp_events(rng, users)
    navigation_events = generate_navigation_sequences(rng, users)

    users.to_csv(RAW_DIR / "users.csv", index=False)
    exercises.to_csv(RAW_DIR / "exercises.csv", index=False)
    exercise_attempts.to_csv(RAW_DIR / "exercise_attempts.csv", index=False)
    challenge_attempts.to_csv(RAW_DIR / "challenge_attempts.csv", index=False)
    platform_load.to_csv(RAW_DIR / "platform_load.csv", index=False)
    xp_events.to_csv(RAW_DIR / "xp_events.csv", index=False)
    navigation_events.to_csv(RAW_DIR / "navigation_events.csv", index=False)

    print("Datasets simulados generados en", RAW_DIR)
    for name, df in [
        ("users", users), ("exercises", exercises), ("exercise_attempts", exercise_attempts),
        ("challenge_attempts", challenge_attempts), ("platform_load", platform_load),
        ("xp_events", xp_events), ("navigation_events", navigation_events),
    ]:
        print(f"  {name}: {len(df):,} filas, {df.shape[1]} columnas")


if __name__ == "__main__":
    main()
