import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "ml")]
# Tests use a throwaway database so they never touch db/thermotwin.db
os.environ["TT_DB"] = str(Path(tempfile.mkdtemp()) / "test.db")
os.environ["TT_MODE"] = "local"
