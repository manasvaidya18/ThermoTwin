"""inference-service HTTP API (port 8102 when run on its own)."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .service import InferenceService

app = FastAPI(title="ThermoTwin inference-service")
_svc: InferenceService | None = None


def svc() -> InferenceService:
    global _svc
    if _svc is None:
        _svc = InferenceService()
    return _svc


class ScoreRequest(BaseModel):
    fridges: list[dict]       # [{id, cls}]
    readings: list[dict]      # [{fridge_id, tick, minute, temp_c}]


@app.get("/health")
def health() -> dict:
    return {"service": "inference", "ok": True}


@app.get("/info")
def info() -> dict:
    return svc().info()


@app.post("/score")
def score(req: ScoreRequest) -> dict:
    return svc().score(req.fridges, req.readings)
