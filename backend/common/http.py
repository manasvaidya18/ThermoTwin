"""Small HTTP helpers for service-to-service calls (used only in TT_MODE=http)."""
from __future__ import annotations

import time

import httpx


class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self.base = base_url.rstrip("/")
        self.http = httpx.Client(timeout=timeout)

    def get(self, path: str, **params):
        r = self.http.get(self.base + path, params={k: v for k, v in params.items() if v is not None})
        r.raise_for_status()
        return r.json()

    def post(self, path: str, body: dict):
        r = self.http.post(self.base + path, json=body)
        r.raise_for_status()
        return r.json()

    def wait_ready(self, tries: int = 60, delay: float = 1.0) -> None:
        for _ in range(tries):
            try:
                if self.http.get(self.base + "/health", timeout=3).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(delay)
        raise RuntimeError(f"service at {self.base} did not become ready")
