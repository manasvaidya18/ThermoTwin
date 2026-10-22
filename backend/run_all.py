"""Start ThermoTwin in one process (gateway + telemetry + inference + alerts) on http://localhost:8080.

This is the demo mode: one command, one port, no network between services.
Usage:  python backend/run_all.py [port]
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("TT_MODE", "local")

import uvicorn  # noqa: E402

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8080))
    from backend.services.gateway.app import app  # noqa: E402  (loads the models and scores the demo fleet)
    print(f"ThermoTwin at http://localhost:{port}  (all services in one process; Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
