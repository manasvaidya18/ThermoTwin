"""Start the live ThermoTwin demo (API + UI) on http://localhost:8080, from any working directory."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import uvicorn  # noqa: E402

from thermotwin.api import app  # noqa: E402

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"ThermoTwin live demo at http://localhost:{port}  (Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
