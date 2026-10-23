"""Service client manager for ThermoTwin Django Core Backend.

Divides roles cleanly:
- Telemetry: In-process TelemetryService (reads/writes SQLite / PostgreSQL).
- Inference: Calls FastAPI ML service at http://127.0.0.1:8102.
             Gracefully falls back to in-process ML service if FastAPI is not yet started in local mode.
- Alerts: AlertService evaluating clinical safety rules from telemetry + inference scores.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from backend.common import config
from backend.common.http import ServiceClient
from backend.services.alerts.service import AlertService
from backend.services.telemetry.service import TelemetryService

logger = logging.getLogger(__name__)


class InferenceHttp:
    """Client for FastAPI ML Inference microservice running on port 8102."""

    def __init__(self, url: str) -> None:
        self.url = url.rstrip("/")
        self.c = ServiceClient(url)

    def score(self, fridges: list[dict], readings: list[dict]) -> dict:
        return self.c.post("/score", {"fridges": fridges, "readings": readings})

    def health(self) -> dict:
        try:
            return self.c.get("/health")
        except Exception as e:
            return {"service": "inference", "ok": False, "error": str(e)}


class ServiceManager:
    """Lazy manager for telemetry, inference, and alert services."""

    def __init__(self) -> None:
        self._telemetry: TelemetryService | None = None
        self._inference = None
        self._alerts: AlertService | None = None

    @property
    def telemetry(self) -> TelemetryService:
        if self._telemetry is None:
            self._telemetry = TelemetryService()
            self._telemetry.health = lambda: {"service": "telemetry", "ok": True, "mode": "django"}
        return self._telemetry

    @property
    def inference(self):
        if self._inference is None:
            url = os.environ.get("TT_INFERENCE_URL", config.INFERENCE_URL)
            client = InferenceHttp(url)
            # Check if FastAPI ML microservice is available
            try:
                res = client.c.http.get(f"{client.url}/health", timeout=1.5)
                if res.status_code == 200:
                    self._inference = client
                    return self._inference
            except Exception:
                pass

            # Fallback for pure standalone local runs if FastAPI service is not started
            from backend.services.inference.service import InferenceService
            self._inference = InferenceService()
        return self._inference

    @property
    def alerts(self) -> AlertService:
        if self._alerts is None:
            self._alerts = AlertService(self.telemetry, self.inference)
            self._alerts.has = lambda fid, t: fid in self._alerts.meta
            self._alerts.health = lambda: {"service": "alerts", "ok": True, "mode": "django"}
        return self._alerts


manager = ServiceManager()
