#!/usr/bin/env python
"""Django management: migrate, seed_demo, runserver, createsuperuser, ..."""
import os
import sys
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))           # backend/ (config, apps)
    sys.path.insert(1, str(here.parent))    # repo root (prediction_engine)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
