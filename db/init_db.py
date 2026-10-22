"""Create the ThermoTwin SQLite database from schema.sql and the seed files.

Usage:  python db/init_db.py [--path db/thermotwin.db] [--reset]
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_PATH = HERE / "thermotwin.db"


def init_db(path: str | Path = DEFAULT_PATH, reset: bool = False) -> Path:
    path = Path(path)
    if reset and path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
        for f in sorted((HERE / "seed").glob("*.sql")):
            con.executescript(f.read_text(encoding="utf-8"))
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(DEFAULT_PATH))
    ap.add_argument("--reset", action="store_true", help="delete the database file first")
    a = ap.parse_args()
    p = init_db(a.path, a.reset)
    with sqlite3.connect(p) as con:
        counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for t in ("facilities", "fridges", "vaccines", "fridge_stock", "readings", "alert_events")}
    print(f"Database ready at {p}: {counts}")
