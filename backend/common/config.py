"""Settings shared by all backend services. Every value can be overridden with an environment variable."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = REPO_ROOT / "ml"

# The ML package (ml/thermotwin) is imported by the inference service; make it importable without installing.
for p in (REPO_ROOT, ML_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

MODELS_PATH = Path(os.environ.get("TT_MODELS", ML_ROOT / "artifacts" / "models.pkl"))
DB_PATH = Path(os.environ.get("TT_DB", REPO_ROOT / "db" / "thermotwin.db"))
FRONTEND_DIR = Path(os.environ.get("TT_FRONTEND", REPO_ROOT / "frontend"))
SCENARIO_PATH = Path(os.environ.get("TT_SCENARIO", Path(__file__).resolve().parents[1] / "services" / "telemetry"
                                    / "scenarios" / "pune_demo.json"))

# "local": the gateway runs every service in one process (default, used for the demo).
# "http":  each service runs as its own process and the gateway calls them over HTTP.
MODE = os.environ.get("TT_MODE", "local")
TELEMETRY_URL = os.environ.get("TT_TELEMETRY_URL", "http://127.0.0.1:8101")
INFERENCE_URL = os.environ.get("TT_INFERENCE_URL", "http://127.0.0.1:8102")
ALERTS_URL = os.environ.get("TT_ALERTS_URL", "http://127.0.0.1:8103")
