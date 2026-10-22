"""alerts-service HTTP API (port 8103 when run on its own). Calls telemetry-service and inference-service."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from backend.common import config
from backend.common.http import ServiceClient

from .service import AlertService

app = FastAPI(title="ThermoTwin alerts-service")
_svc: AlertService | None = None


class TelemetryHttp:
    def __init__(self, url: str) -> None:
        self.c = ServiceClient(url)
        self.c.wait_ready()

    def registry(self):
        return self.c.get("/fridges")

    def readings(self):
        return self.c.get("/readings")

    def clock_state(self):
        return self.c.get("/clock")


class InferenceHttp:
    def __init__(self, url: str) -> None:
        self.c = ServiceClient(url)
        self.c.wait_ready()

    def score(self, fridges, readings):
        return self.c.post("/score", {"fridges": fridges, "readings": readings})


def svc() -> AlertService:
    global _svc
    if _svc is None:
        _svc = AlertService(TelemetryHttp(config.TELEMETRY_URL), InferenceHttp(config.INFERENCE_URL))
    return _svc


def _check(fid: str) -> None:
    if fid not in svc().meta:
        raise HTTPException(404, f"unknown fridge {fid}")


@app.get("/health")
def health() -> dict:
    return {"service": "alerts", "ok": True, "ready": _svc is not None}


@app.get("/fleet")
def fleet(tick: int) -> list[dict]:
    return svc().fleet(tick)


@app.get("/fridges/{fid}")
def detail(fid: str, tick: int, hours: int = 24) -> dict:
    _check(fid)
    return svc().detail(fid, tick, hours)


@app.get("/fridges/{fid}/summary")
def summary(fid: str, tick: int) -> dict:
    _check(fid)
    return svc().summary(fid, tick)


@app.get("/history")
def history(tick: int, fridge_id: str | None = None) -> list[dict]:
    return svc().history(tick, fridge_id)
