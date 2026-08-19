"""
Tutunaku - Pruebas del simulador de datos (Etapa 16.2 de la guía).

Verifica reproducibilidad (semilla 2026), rangos válidos, ausencia de
duplicados exactos no intencionales, y coherencia de las reglas de negocio
usadas en `simulation/generate_dataset.py`.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from simulation import generate_dataset as sim  # noqa: E402


@pytest.fixture(scope="module")
def rng():
    return np.random.default_rng(sim.SEED)


@pytest.fixture(scope="module")
def users(rng):
    return sim.generate_users(rng, n_users=200)


@pytest.fixture(scope="module")
def exercises(rng):
    return sim.generate_exercises(rng, n_exercises=50)


def test_users_reproducible_with_fixed_seed():
    df1 = sim.generate_users(np.random.default_rng(sim.SEED), n_users=100)
    df2 = sim.generate_users(np.random.default_rng(sim.SEED), n_users=100)
    assert df1.equals(df2)


def test_users_connectivity_in_range(users):
    assert users["base_connectivity_score"].between(0.0, 1.0).all()


def test_users_no_nulls(users):
    assert users.isna().sum().sum() == 0


def test_exercises_difficulty_in_expected_range(exercises):
    assert exercises["difficulty"].between(1, 5).all()
    assert (exercises["base_time_seconds"] > 0).all()


def test_exercise_attempts_time_always_positive(rng, users, exercises):
    attempts = sim.generate_exercise_attempts(rng, users, exercises, n_attempts=2000)
    assert (attempts["time_spent_seconds"] > 0).all()
    assert attempts["difficulty"].between(1, 5).all()


def test_exercise_attempts_has_intentional_missing_and_duplicates(rng, users, exercises):
    """La simulación inyecta casos faltantes/duplicados a propósito (Etapa 5).

    Los duplicados simulan un reintento de red que repite la misma fila (mismo
    attempt_id incluido); es tarea del ETL (`transform_exercise_attempts`)
    colapsarlos por clave natural, no de la simulación entregarlos limpios.
    """
    attempts = sim.generate_exercise_attempts(rng, users, exercises, n_attempts=5000)
    assert attempts["connectivity_quality"].isna().sum() > 0
    # hay filas de intento duplicadas por reintento de red (mismo user/exercise/timestamp)
    assert attempts.duplicated(subset=["user_id", "exercise_id", "timestamp", "attempt_number"]).sum() > 0


def test_challenge_attempts_hearts_within_bounds(rng, users):
    challenges = sim.generate_challenge_attempts(rng, users, n_challenges=1000)
    assert challenges["hearts_end"].between(0, 5).all()
    assert challenges["completed_with_lives"].dtype == bool


def test_platform_load_has_daily_seasonality():
    rng_local = np.random.default_rng(sim.SEED)
    load = sim.generate_platform_load(rng_local, n_days=14)
    by_hour = load.groupby("hour_of_day")["active_users"].mean()
    # el pico esperado (≈20h) debe superar claramente al valle esperado (≈4h)
    assert by_hour.loc[20] > by_hour.loc[4] * 1.3


def test_xp_events_anomalies_are_flagged_and_minority(rng, users):
    xp = sim.generate_xp_events(rng, users, n_events=5000)
    anomaly_rate = xp["is_anomaly_injected"].mean()
    assert 0 < anomaly_rate < 0.10  # las anomalías deben ser minoría, no la norma
    assert (xp["xp_gained"] > 0).all()


def test_navigation_sequences_start_home_end_salir(rng, users):
    nav = sim.generate_navigation_sequences(rng, users, n_sessions=50)
    first_steps = nav.sort_values(["session_id", "step_index"]).groupby("session_id").first()
    last_steps = nav.sort_values(["session_id", "step_index"]).groupby("session_id").last()
    assert (first_steps["page"] == "home").all()
    assert (last_steps["page"] == "salir").all()
