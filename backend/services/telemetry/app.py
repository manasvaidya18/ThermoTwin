"""telemetry-service HTTP API (port 8101 when run on its own)."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .service import TelemetryService

app = FastAPI(title="ThermoTwin telemetry-service")
_svc: TelemetryService | None = None


def svc() -> TelemetryService:
    global _svc
    if _svc is None:
        _svc = TelemetryService()
    return _svc


class ClockAction(BaseModel):
    action: str
    ticks: int = 1
    seconds_per_tick: float | None = None


@app.get("/health")
def health() -> dict:
    return {"service": "telemetry", "ok": True, "source": svc().source}


@app.get("/fridges")
def fridges() -> list[dict]:
    return svc().registry()


@app.get("/readings")
def readings() -> list[dict]:
    return svc().readings()


@app.get("/clock")
def clock() -> dict:
    return svc().clock_state()


@app.post("/clock")
def clock_action(a: ClockAction) -> dict:
    try:
        return svc().clock_action(a.action, a.ticks, a.seconds_per_tick)
    except ValueError as e:
        raise HTTPException(400, str(e))
