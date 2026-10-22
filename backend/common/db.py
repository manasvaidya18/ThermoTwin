"""SQLite access shared by the services. The schema and seed data live in the top-level db/ folder."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from db.init_db import init_db

from .config import DB_PATH


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    if not Path(path).exists():
        init_db(path)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def vaccine_catalogue(con: sqlite3.Connection) -> dict[str, bool]:
    return {r["name"]: bool(r["freeze_sensitive"]) for r in con.execute("SELECT name, freeze_sensitive FROM vaccines")}
