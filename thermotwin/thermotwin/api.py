"""ThermoTwin API and demo server.

Serves the live model over JSON and the demo UI from ../ui/app on the same port, so the UI can call /api/*.

Run:  python -m thermotwin.api            (http://localhost:8080)
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from .live import LiveEngine  # noqa: E402

UI_DIR = Path(__file__).resolve().parents[2] / "ui" / "app"

app = FastAPI(title="ThermoTwin API", version="0.1.0")
engine = LiveEngine()


@app.middleware("http")
async def no_cache(request, call_next):
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-store"
    return resp


class ClockAction(BaseModel):
    action: str                 # play | pause | reset | step
    ticks: int = 1              # for step: number of 10-minute readings (negative goes back)
    seconds_per_tick: float | None = None


@app.get("/api/state")
def state() -> dict:
    return engine.state()


@app.post("/api/clock")
def clock(a: ClockAction) -> dict:
    c = engine.clock
    if a.seconds_per_tick:
        c.seconds_per_tick = max(0.2, a.seconds_per_tick)
    if a.action == "play":
        c.play()
    elif a.action == "pause":
        c.pause()
    elif a.action == "reset":
        c.reset()
    elif a.action == "step":
        c.step(a.ticks)
    else:
        raise HTTPException(400, "action must be play, pause, reset or step")
    return engine.state()


@app.get("/api/fridges")
def fridges() -> dict:
    return {"state": engine.state(), "fridges": engine.fleet()}


@app.get("/api/fridges/{fid}")
def fridge(fid: str, hours: int = 24) -> dict:
    if fid not in engine.ids:
        raise HTTPException(404, f"unknown fridge {fid}")
    return engine.detail(fid, hours=max(1, min(hours, 48)))


@app.get("/api/alerts")
def alerts() -> dict:
    return {"state": engine.state(), "alerts": [f for f in engine.fleet() if f["tier"] != "Normal"]}


@app.get("/")
def root():
    return RedirectResponse("/index.html")


if UI_DIR.exists():
    app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8080)), log_level="warning")
