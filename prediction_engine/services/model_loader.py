"""Load the trained models (models/models.pkl).

The file holds the freeze and heat hazard models, the cause classifier, the degradation model and the alert thresholds.
Files saved before the restructure refer to the old package name (thermotwin.*); the unpickler maps those names to
their new homes, so old model files keep working without retraining.
"""
from __future__ import annotations

import pickle
from pathlib import Path

from prediction_engine.app.config import MODELS_PATH

MODULE_MAP = {
    "thermotwin.model": "prediction_engine.services.risk_service",
    "thermotwin.cause": "prediction_engine.services.risk_service",
    "thermotwin.degradation": "prediction_engine.services.maintenance_service",
    "thermotwin.features": "prediction_engine.ingestion.preprocessing",
    "thermotwin.twin": "prediction_engine.digital_twin.virtual_vial",
    "thermotwin.deep": "prediction_engine.training.deep",
}


class _Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        return super().find_class(MODULE_MAP.get(module, module), name)


def load_models(path: Path = MODELS_PATH) -> dict:
    with open(path, "rb") as f:
        return _Unpickler(f).load()


def save_models(models: dict, path: Path = MODELS_PATH) -> None:
    with open(path, "wb") as f:
        pickle.dump(models, f)
