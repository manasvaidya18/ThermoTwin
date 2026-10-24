"""How the backend reaches the prediction engine.

If TT_ENGINE_URL is set and the engine answers, readings are scored over HTTP (separate FastAPI service).
Otherwise the same PredictionService runs inside the Django process (demo default: one command, one port).
"""
from __future__ import annotations

import logging

from django.conf import settings

log = logging.getLogger(__name__)
_local = None


def _local_engine():
    global _local
    if _local is None:
        from prediction_engine.services.prediction_service import PredictionService
        _local = PredictionService()
    return _local


def _http():
    if not settings.ENGINE_URL:
        return None
    import httpx
    try:
        c = httpx.Client(base_url=settings.ENGINE_URL.rstrip("/"), timeout=180)
        if c.get("/health", timeout=2).status_code == 200:
            return c
    except Exception as e:      # noqa: BLE001 - fall back to in-process scoring
        log.warning("prediction engine at %s not reachable (%s); scoring in-process", settings.ENGINE_URL, e)
    return None


def mode() -> str:
    return "http" if _http() else "in_process"


def score(fridges: list[dict], readings: list[dict]) -> dict:
    c = _http()
    if c is not None:
        r = c.post("/score", json={"fridges": fridges, "readings": readings})
        r.raise_for_status()
        return r.json()
    return _local_engine().score(fridges, readings)
