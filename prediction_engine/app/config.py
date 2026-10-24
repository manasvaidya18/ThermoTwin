"""Prediction engine settings (all overridable by environment variables)."""
from __future__ import annotations

import os
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parents[1]
MODELS_PATH = Path(os.environ.get("TT_MODELS", ENGINE_ROOT / "models" / "models.pkl"))
HOST = os.environ.get("TT_ENGINE_HOST", "127.0.0.1")
PORT = int(os.environ.get("TT_ENGINE_PORT", 8102))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
