"""API gateway: the only service the frontend talks to. Serves /api/* and the frontend files on one port.

Public API (unchanged from the original demo):
  GET  /api/state                    demo clock
  POST /api/clock {action, ticks}    play | pause | reset | step
  GET  /api/fridges                  all fridges with tier, Virtual Vial, risk, cause
  GET  /api/fridges/{id}?hours=24    one fridge with history and forecast
  GET  /api/alerts                   fridges not in Normal
  GET  /api/alerts/history           tier changes so far (from the database)
  GET  /api/health                   status of the services behind the gateway
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.common import config

from .clients import build_clients

app = FastAPI(title="ThermoTwin API gateway", version="0.2.0")
telemetry, alerts = build_clients()


@app.middleware("http")
async def no_cache(request, call_next):
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-store"
    return resp


class ClockAction(BaseModel):
    action: str                 # play | pause | reset | step
    ticks: int = 1              # for step: number of 10-minute readings (negative goes back)
    seconds_per_tick: float | None = None


def _state() -> dict:
    s = dict(telemetry.clock_state())
    s.pop("source", None)
    return s


@app.get("/api/state")
def state() -> dict:
    return _state()


@app.post("/api/clock")
def clock(a: ClockAction) -> dict:
    if a.action not in ("play", "pause", "reset", "step"):
        raise HTTPException(400, "action must be play, pause, reset or step")
    telemetry.clock_action(a.action, a.ticks, a.seconds_per_tick)
    return _state()


@app.get("/api/fridges")
def fridges() -> dict:
    s = _state()
    return {"state": s, "fridges": alerts.fleet(s["tick"])}


@app.get("/api/fridges/{fid}")
def fridge(fid: str, hours: int = 24) -> dict:
    t = _state()["tick"]
    if not alerts.has(fid, t):
        raise HTTPException(404, f"unknown fridge {fid}")
    return alerts.detail(fid, t, hours=max(1, min(hours, 48)))


@app.get("/api/alerts")
def active_alerts() -> dict:
    s = _state()
    return {"state": s, "alerts": [f for f in alerts.fleet(s["tick"]) if f["tier"] != "Normal"]}


@app.get("/api/alerts/history")
def alert_history(fridge_id: str | None = None) -> dict:
    s = _state()
    return {"state": s, "events": alerts.history(s["tick"], fridge_id)}


@app.get("/api/health")
def health() -> dict:
    out = {"gateway": {"ok": True, "mode": config.MODE}}
    for name, c in (("telemetry", telemetry), ("alerts", alerts)):
        try:
            out[name] = c.health()
        except Exception as e:      # noqa: BLE001 - report, don't fail the health page
            out[name] = {"ok": False, "error": str(e)}
    return out


@app.get("/")
def root():
    return RedirectResponse("/index.html")


if config.FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
