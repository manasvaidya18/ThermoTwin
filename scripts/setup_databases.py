"""One-time database setup from .env: PostgreSQL database + tables + demo data, and the InfluxDB bucket.

  python scripts/setup_databases.py

1. Creates the PostgreSQL database POSTGRES_DB if it does not exist (connects to the 'postgres' database first).
2. Runs Django migrations and seed_demo.
3. Checks InfluxDB (INFLUX_URL / INFLUX_TOKEN / INFLUX_ORG) and creates INFLUX_BUCKET if it is missing.
Credentials are read from .env / the environment and never printed.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def postgres() -> bool:
    db = os.environ.get("POSTGRES_DB")
    if not db:
        print("PostgreSQL: POSTGRES_DB not set in .env, Django will use SQLite")
        return True
    import psycopg
    from psycopg import sql
    params = dict(user=os.environ.get("POSTGRES_USER", "postgres"), password=os.environ.get("POSTGRES_PASSWORD", ""),
                  host=os.environ.get("POSTGRES_HOST", "127.0.0.1"), port=os.environ.get("POSTGRES_PORT", "5432"))
    try:
        with psycopg.connect(dbname="postgres", autocommit=True, **params) as con:
            exists = con.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,)).fetchone()
            if not exists:
                con.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db)))
                print(f"PostgreSQL: created database {db}")
            else:
                print(f"PostgreSQL: database {db} exists")
        return True
    except Exception as e:      # noqa: BLE001
        print(f"PostgreSQL: could not connect ({type(e).__name__}: {str(e).splitlines()[0]}). Check POSTGRES_* in .env")
        return False


def influx() -> None:
    url, token = os.environ.get("INFLUX_URL"), os.environ.get("INFLUX_TOKEN")
    if not url or not token:
        print("InfluxDB: INFLUX_URL / INFLUX_TOKEN not set, readings will be stored in PostgreSQL")
        return
    from influxdb_client import InfluxDBClient
    org, bucket = os.environ.get("INFLUX_ORG", "thermotwin"), os.environ.get("INFLUX_BUCKET", "thermotwin")
    try:
        with InfluxDBClient(url=url, token=token, org=org) as c:
            if not c.ping():
                print(f"InfluxDB: no answer at {url}")
                return
            api = c.buckets_api()
            if api.find_bucket_by_name(bucket):
                print(f"InfluxDB: bucket {bucket} exists")
            else:
                api.create_bucket(bucket_name=bucket, org=org)
                print(f"InfluxDB: created bucket {bucket}")
    except Exception as e:      # noqa: BLE001
        print(f"InfluxDB: {type(e).__name__}: {str(e).splitlines()[0][:200]}. Check INFLUX_* in .env")


def main() -> None:
    load_env()
    ok = postgres()
    influx()
    if ok:
        manage = [sys.executable, str(ROOT / "backend" / "manage.py")]
        subprocess.run(manage + ["migrate", "-v", "1"], cwd=ROOT, check=True)
        subprocess.run(manage + ["seed_demo"], cwd=ROOT, check=True)
        print("Done. Start with: python scripts/run_demo.py")


if __name__ == "__main__":
    main()
