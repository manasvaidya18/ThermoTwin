"""Start ThermoTwin with Django Core + FastAPI ML microservice.

- FastAPI (ML Inference) on http://127.0.0.1:8102
- Django (Core, Gateway & UI) on http://localhost:8080

Usage:
  python run_django.py [port]
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DJANGO_DIR = ROOT / "django_backend"


def main():
    django_port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8080))
    fastapi_port = int(os.environ.get("INFERENCE_PORT", 8102))

    env = dict(
        os.environ,
        PYTHONPATH=os.pathsep.join([str(ROOT), str(ROOT / "ml"), str(DJANGO_DIR)]),
        TT_INFERENCE_URL=f"http://127.0.0.1:{fastapi_port}",
    )

    venv_py = ROOT / "venv" / "Scripts" / "python.exe"
    py_exec = str(venv_py) if venv_py.exists() else sys.executable

    print("=" * 60)
    print(" ThermoTwin: Django Core + FastAPI ML Service")
    print(f" Python Executable: {py_exec}")
    print("=" * 60)

    # 1. Start FastAPI ML Service on port 8102
    print(f"[*] Starting FastAPI ML Inference on http://127.0.0.1:{fastapi_port}...")
    fastapi_proc = subprocess.Popen(
        [
            py_exec,
            "-m",
            "uvicorn",
            "backend.services.inference.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(fastapi_port),
            "--log-level",
            "warning",
        ],
        cwd=ROOT,
        env=env,
    )

    # Wait brief moment for ML service to bind
    time.sleep(1.5)

    # 2. Start Django Core on port 8080
    print(f"[*] Starting Django Core Backend on http://localhost:{django_port}...")
    django_proc = subprocess.Popen(
        [
            py_exec,
            str(DJANGO_DIR / "manage.py"),
            "runserver",
            f"127.0.0.1:{django_port}",
            "--noreload",
        ],
        cwd=DJANGO_DIR,
        env=env,
    )

    print("=" * 60)
    print(f" Dashboard ready at: http://localhost:{django_port}")
    print(" Press Ctrl+C to stop both services.")
    print("=" * 60)

    try:
        while True:
            if fastapi_proc.poll() is not None:
                print("[!] FastAPI process terminated.")
                break
            if django_proc.poll() is not None:
                print("[!] Django process terminated.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Stopping services...")
    finally:
        for p in (fastapi_proc, django_proc):
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                pass
        print("[+] All services stopped.")


if __name__ == "__main__":
    main()
