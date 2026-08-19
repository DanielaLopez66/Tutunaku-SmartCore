"""
Tutunaku - Registro de modelos de Machine Learning.

Carga en memoria (una sola vez, caché de proceso) los artefactos serializados
por los notebooks (`models/serialized/*.joblib` + `*_metadata.json`). Si un
modelo falta o está corrupto, NO se lanza excepción al importar el módulo: se
registra el error y ese modelo queda marcado como no disponible, para que la
aplicación principal siga funcionando y solo falle (503) la ruta que lo
necesite. Ver Etapa 13: "Manejar fallos para que la aplicación principal no
caiga si el modelo falla".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import joblib
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# nombre_modelo -> (archivo_joblib, archivo_metadata)
MODEL_FILES: dict[str, tuple[str, str]] = {
    "time_estimator": ("time_estimator.joblib", "time_estimator_metadata.json"),
    "success_classifier": ("success_classifier.joblib", "success_classifier_metadata.json"),
    "platform_load_forecaster": ("platform_load_forecaster.joblib", "platform_load_forecaster_metadata.json"),
    "anomaly_detector": ("anomaly_detector.joblib", "anomaly_detector_metadata.json"),
    "navigation_markov": ("navigation_markov.joblib", "navigation_markov_metadata.json"),
    "rfm_kmeans": ("rfm_kmeans.joblib", "rfm_kmeans_metadata.json"),
}


@dataclass
class LoadedModel:
    name: str
    artifact: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    loaded: bool = False
    error: Optional[str] = None


@dataclass
class ModelRegistry:
    model_dir: Path
    models: dict[str, LoadedModel] = field(default_factory=dict)
    _initialized: bool = False

    def load_all(self) -> None:
        for name, (joblib_file, meta_file) in MODEL_FILES.items():
            self.models[name] = self._load_one(name, joblib_file, meta_file)
        self._initialized = True
        loaded_count = sum(1 for m in self.models.values() if m.loaded)
        logger.info("ml_model_registry_loaded", loaded=loaded_count, total=len(MODEL_FILES))

    def _load_one(self, name: str, joblib_file: str, meta_file: str) -> LoadedModel:
        joblib_path = self.model_dir / joblib_file
        meta_path = self.model_dir / meta_file
        try:
            artifact = joblib.load(joblib_path)
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            logger.info("ml_model_loaded", model=name, path=str(joblib_path))
            return LoadedModel(name=name, artifact=artifact, metadata=metadata, loaded=True)
        except Exception as exc:  # noqa: BLE001 - se documenta y aísla a propósito
            logger.warning("ml_model_load_failed", model=name, path=str(joblib_path), error=str(exc))
            return LoadedModel(name=name, loaded=False, error=str(exc))

    def get(self, name: str) -> LoadedModel:
        if not self._initialized:
            self.load_all()
        return self.models.get(name, LoadedModel(name=name, loaded=False, error="modelo desconocido"))

    def all_info(self) -> list[LoadedModel]:
        if not self._initialized:
            self.load_all()
        return list(self.models.values())


_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry(model_dir=Path(settings.ML_MODEL_DIR))
        _registry.load_all()
    return _registry
