"""Prediction engine HTTP API (FastAPI).

Run on its own:  python -m uvicorn prediction_engine.app.main:app --port 8102   (from the repo root)
The Django backend calls it at TT_ENGINE_URL, or runs the same PredictionService in-process if it is not running.
"""
from __future__ import annotations

from fastapi import FastAPI

from prediction_engine.app.schemas import ScoreRequest, ScoreResponse, ValidateRequest
from prediction_engine.ingestion.data_validator import validate_readings
from prediction_engine.services.prediction_service import PredictionService

app = FastAPI(title="ThermoTwin prediction engine", version="0.3.0")
_svc: PredictionService | None = None


def svc() -> PredictionService:
    global _svc
    if _svc is None:
        _svc = PredictionService()
    return _svc


@app.get("/health")
def health() -> dict:
    return {"service": "prediction_engine", "ok": True}


@app.get("/info")
def info() -> dict:
    return svc().info()


@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> dict:
    return svc().score([f.model_dump() for f in req.fridges], [r.model_dump() for r in req.readings])


@app.post("/validate")
def validate(req: ValidateRequest) -> dict:
    clean, errors = validate_readings([r.model_dump() for r in req.readings])
    return {"accepted": len(clean), "errors": errors}
