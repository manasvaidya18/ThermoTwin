"""How the gateway reaches the other services.

local mode: the services run inside the gateway process (one port, used for the demo).
http mode:  each service is its own process; the gateway calls it over HTTP.
Both expose the same methods, so the gateway code does not change between modes.
"""
from __future__ import annotations

from backend.common import config
from backend.common.http import ServiceClient


class TelemetryHttp:
    def __init__(self, url: str) -> None:
        self.c = ServiceClient(url)

    def clock_state(self) -> dict:
        return self.c.get("/clock")

    def clock_action(self, action: str, ticks: int = 1, seconds_per_tick: float | None = None) -> dict:
        return self.c.post("/clock", {"action": action, "ticks": ticks, "seconds_per_tick": seconds_per_tick})

    def health(self) -> dict:
        return self.c.get("/health")


class AlertsHttp:
    def __init__(self, url: str) -> None:
        self.c = ServiceClient(url)

    def fleet(self, t: int) -> list[dict]:
        return self.c.get("/fleet", tick=t)

    def detail(self, fid: str, t: int, hours: int = 24) -> dict:
        return self.c.get(f"/fridges/{fid}", tick=t, hours=hours)

    def history(self, t: int, fridge_id: str | None = None) -> list[dict]:
        return self.c.get("/history", tick=t, fridge_id=fridge_id)

    def has(self, fid: str, t: int) -> bool:
        return any(f["id"] == fid for f in self.fleet(t))

    def health(self) -> dict:
        return self.c.get("/health")


class _Local:
    """Wraps the in-process services with the same interface as the HTTP clients."""

    def __init__(self) -> None:
        from backend.services.alerts.service import AlertService
        from backend.services.inference.service import InferenceService
        from backend.services.telemetry.service import TelemetryService

        self.telemetry = TelemetryService()
        self.inference = InferenceService()
        self.alerts = AlertService(self.telemetry, self.inference)
        self.alerts.has = lambda fid, t: fid in self.alerts.meta
        for s, name in ((self.telemetry, "telemetry"), (self.alerts, "alerts")):
            s.health = (lambda n: lambda: {"service": n, "ok": True, "mode": "local"})(name)


def build_clients():
    """Return (telemetry, alerts) clients for the configured mode."""
    if config.MODE == "http":
        return TelemetryHttp(config.TELEMETRY_URL), AlertsHttp(config.ALERTS_URL)
    local = _Local()
    return local.telemetry, local.alerts
