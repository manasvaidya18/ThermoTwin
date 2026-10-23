"""ASGI config for ThermoTwin project."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application

DJANGO_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = DJANGO_DIR.parent
for p in (DJANGO_DIR, REPO_ROOT, REPO_ROOT / "ml"):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tt_core.settings")
application = get_asgi_application()
