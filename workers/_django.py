"""Shared setup for the workers: load Django (backend/) so workers use the same models and services."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def setup() -> None:
    for p in (ROOT / "backend", ROOT):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()


def run(job, interval: float | None) -> None:
    """Run job once, or every `interval` seconds until Ctrl+C."""
    while True:
        job()
        if not interval:
            return
        time.sleep(interval)
