"""Start ThermoTwin: Django backend (API + website + phone app) and the FastAPI prediction engine.

  python scripts/run_demo.py [port]          http://localhost:8080 (default)
  python scripts/run_demo.py 8080 --no-engine   Django only (scores in-process)

Steps: migrate -> seed_demo -> prediction engine on TT_ENGINE_PORT (8102) -> Django on [port]. Ctrl+C stops both.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANAGE = [sys.executable, str(ROOT / "backend" / "manage.py")]


def wait_ready(url: str, seconds: int = 60) -> bool:
    for _ in range(seconds):
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    port = int(args[0]) if args else int(os.environ.get("PORT", 8080))
    use_engine = "--no-engine" not in sys.argv
    engine_port = int(os.environ.get("TT_ENGINE_PORT", 8102))
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(ROOT), str(ROOT / "backend")]))

    subprocess.run(MANAGE + ["migrate", "-v", "0"], cwd=ROOT, env=env, check=True)
    subprocess.run(MANAGE + ["seed_demo"], cwd=ROOT, env=env, check=True)

    procs = []
    if use_engine:
        procs.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "prediction_engine.app.main:app",
                                       "--host", "127.0.0.1", "--port", str(engine_port), "--log-level", "warning"],
                                      cwd=ROOT, env=env))
        url = f"http://127.0.0.1:{engine_port}"
        if wait_ready(url + "/health"):
            env["TT_ENGINE_URL"] = url
            print(f"prediction engine (FastAPI) at {url}")
        else:
            print("prediction engine did not start; Django will score in-process")
            env["TT_ENGINE_URL"] = ""
    else:
        env["TT_ENGINE_URL"] = ""
    procs.append(subprocess.Popen(MANAGE + ["runserver", f"127.0.0.1:{port}", "--noreload"], cwd=ROOT, env=env))
    print(f"ThermoTwin at http://localhost:{port}  (website, phone app and /api). Ctrl+C stops everything.")
    print("The first page load takes about 15 s while the models score the demo fridges.")
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
