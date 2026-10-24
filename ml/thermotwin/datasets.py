"""Loaders that turn public datasets into ThermoTwin's standard format.

Standard log format (same as the simulator): one row per unit per 10-minute reading with columns
unit, tick, minute, air_meas, plus any ground truth the dataset has (prod_true, ambient).
Units table: unit, cls, name.

Datasets (downloaded into ml/data/external/, not committed):
  bangkok       123 domestic fridges, Bangkok, 5 days at 5-min steps. Air at several shelf positions, ambient,
                and a meat-simulating gel probe (product temperature, 0.5 °C steps). DOI 10.57745/TMWYBQ,
                licence CC BY-NC-SA 4.0 (validation only, credit the authors).
  ult_freezers  Ultra-low temperature freezers, Danish National Biobank (Revco), chamber temperature at 1-min steps
                with door events and faults dated from service reports. Figshare 10.6084/m9.figshare.c.6805332,
                licence CC0.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

EXTERNAL = Path(__file__).resolve().parents[1] / "data" / "external"


def load_bangkok(root: Path = EXTERNAL / "bangkok" / "raw", air_col: str = "T_MS") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bangkok household fridges as 10-minute readings.

    air_col: which air probe plays the role of the logger (middle shelf by default, where stock usually sits).
    Every second 5-minute reading is kept, so the twin runs at its native 10-minute step.
    """
    files = sorted(f for f in Path(root).glob("*.txt") if f.name[:3].isdigit() and f.stat().st_size > 0)
    logs, units = [], []
    for u, f in enumerate(files):
        d = pd.read_csv(f, sep="\t")
        d = d.iloc[1::2].reset_index(drop=True)              # 5 min -> 10 min (reading at the end of each interval)
        logs.append(pd.DataFrame({
            "unit": u, "tick": np.arange(len(d)), "minute": (np.arange(len(d)) + 1) * 10,
            "air_meas": d[air_col].astype(float), "prod_true": d["TP"].astype(float),
            "ambient": d["T_AMB"].astype(float)}))
        units.append(dict(unit=u, cls="DOMESTIC", name=f.stem, fridge_type=f.stem.split("_")[1]))
    return pd.concat(logs, ignore_index=True), pd.DataFrame(units)


ULT_ROOT = EXTERNAL / "ult_freezers"


def read_ult_month(path: Path) -> pd.DataFrame:
    """One Revco monthly temperature log (1-minute rows). Returns Datetime, RTD (chamber °C) and SetPoint."""
    lines = Path(path).read_text(encoding="latin-1").splitlines()
    head = next(i for i, l in enumerate(lines) if l.startswith("Start"))
    cols = [c for c in lines[head].split("\t") if c]
    rows = [l.split("\t")[: len(cols)] for l in lines[head + 1:] if l.startswith("SX")]
    d = pd.DataFrame(rows, columns=cols)
    out = pd.DataFrame({"Datetime": pd.to_datetime(d["Date"] + " " + d["Time"], format="%m/%d/%Y %H:%M:%S", errors="coerce"),
                        "RTD": pd.to_numeric(d["RTD"], errors="coerce"),
                        "SetPoint": pd.to_numeric(d["SetPoint"], errors="coerce")})
    return out.dropna(subset=["Datetime"])


def load_ult_window(files: list[str], root: Path = ULT_ROOT / "raw") -> pd.DataFrame:
    """Concatenate monthly logs and resample the chamber temperature to 10-minute readings (like a logger)."""
    parts = [read_ult_month(root / f) for f in files if (root / f).exists()]
    if not parts:
        return pd.DataFrame(columns=["Datetime", "RTD"])
    d = pd.concat(parts).drop_duplicates("Datetime").set_index("Datetime").sort_index()
    return d["RTD"].resample("10min").last().reset_index()
