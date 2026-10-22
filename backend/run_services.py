"""Start each ThermoTwin service as its own process (microservice mode).

  telemetry-service  :8101   registry, readings, demo clock      (owns readings in the database)
  inference-service  :8102   twin + risk + cause models          (stateless)
  alerts-service     :8103   Guardian tiers, Cause Cards, history (calls telemetry + inference)
  gateway            :8080   public /api/* and the frontend       (calls telemetry + alerts)

Usage:  python backend/run_services.py      (Ctrl+C stops all four)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    ("telemetry", "backend.services.telemetry.app:app", 8101),
    ("inference", "backend.services.inference.app:app", 8102),
    ("alerts", "backend.services.alerts.app:app", 8103),
    ("gateway", "backend.services.gateway.app:app", int(os.environ.get("PORT", 8080))),
]


def main() -> None:
    env = dict(os.environ, TT_MODE="http", PYTHONPATH=os.pathsep.join([str(ROOT), str(ROOT / "ml")]),
               TT_TELEMETRY_URL="http://127.0.0.1:8101", TT_INFERENCE_URL="http://127.0.0.1:8102",
               TT_ALERTS_URL="http://127.0.0.1:8103")
    procs = []
    for name, target, port in SERVICES:
        procs.append(subprocess.Popen([sys.executable, "-m", "uvicorn", target, "--host", "127.0.0.1", "--port", str(port),
                                       "--log-level", "warning"], cwd=ROOT, env=env))
        print(f"started {name:<10} http://127.0.0.1:{port}")
    print("Open http://localhost:8080 . The first page load takes about 15 s while the models score the fleet.")
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            p.terminate()


if __name__ == "__main__":
    main()
