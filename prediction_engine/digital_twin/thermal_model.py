"""ColdChain Gym: a vectorised 3-node RC simulator of vaccine fridges with injected faults.

Each fridge is three heat nodes:
    air       C_a dT_a/dt = (T_e - T_a)/R_ae + (T_p - T_a)/R_ap + door*(T_amb - T_a)/R_door
    product   C_p dT_p/dt = (T_a - T_p)/R_ap
    enclosure C_e dT_e/dt = (T_amb - T_e)/R_ea + (T_a - T_e)/R_ae - u*Q_c
The compressor (u) cools the enclosure (evaporator / ice lining) and is switched by a thermostat on the air
temperature. Units: C in kJ/K, R in K/kW, Q in kW, time in seconds. Simulation runs at 1-minute steps; the
logger records every 10 minutes, like eVIN.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DT = 60.0          # simulation step, seconds
LOG_EVERY = 10     # logger interval, minutes

# Equipment-class priors ("fleet priors"). Values give a product time constant of about 1 h for a packed ILR
# shelf and a holdover of roughly a day for a healthy ILR at 30 °C.
CLASSES = {
    "ILR": dict(C_a=50.0, C_p=100.0, C_e=600.0, R_ap=36.0, R_ae=12.0, R_ea=1000.0, R_door=40.0, Q_c=0.18),
    "DOMESTIC": dict(C_a=30.0, C_p=60.0, C_e=80.0, R_ap=60.0, R_ae=10.0, R_ea=250.0, R_door=20.0, Q_c=0.40),
}
FAULTS = ["thermostat_cold", "relay_stuck_on", "compressor_wear", "gasket_leak", "power_cut",
          "sensor_stuck", "sensor_drift"]


@dataclass
class FleetConfig:
    n_units: int = 240
    days: int = 21
    seed: int = 0
    domestic_share: float = 0.25
    faults_per_unit_month: float = 3.0
    # Optional scripted fridges for demos: list of dicts with keys cls, setpoint, amb_base, faults (list of fault dicts
    # with start/end in minutes). When given, n_units is taken from its length and random faults are not drawn.
    units_spec: list | None = None


def _ambient(minutes: np.ndarray, base: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Room temperature: per-unit base plus a day-night swing (warmest about 3 pm) and slow weather noise."""
    hours = minutes / 60.0
    diurnal = 5.0 * np.sin(2 * np.pi * (hours[None, :] - 9.0) / 24.0)
    weather = np.cumsum(rng.normal(0, 0.02, size=(base.size, minutes.size)), axis=1)
    weather -= weather.mean(axis=1, keepdims=True)
    return base[:, None] + diurnal + np.clip(weather, -4, 4)


def _doors(n: int, T: int, rng: np.random.Generator) -> np.ndarray:
    """Door open (1) minutes: clinic hours 9:00-16:00, more on Wednesday/Saturday session days."""
    door = np.zeros((n, T), dtype=np.float32)
    day_min = np.arange(T) % 1440
    day_idx = np.arange(T) // 1440
    open_hours = (day_min >= 540) & (day_min < 960)
    session = np.isin(day_idx % 7, (2, 5))
    rate = np.where(open_hours, np.where(session, 4.0, 1.5) / 60.0, 0.02 / 60.0)  # openings per minute
    starts = rng.random((n, T)) < rate[None, :]
    lengths = rng.integers(1, 4, size=(n, T))
    for i, t in zip(*np.nonzero(starts)):
        door[i, t:t + lengths[i, t]] = 1.0
    # A few doors left ajar (10-40 min) per unit-month
    for i in range(n):
        for _ in range(rng.poisson(0.6 * T / 43200)):
            t = rng.integers(0, T - 60)
            door[i, t:t + rng.integers(10, 41)] = 1.0
    return door


def _fault_schedule(n: int, T: int, cfg: FleetConfig, rng: np.random.Generator) -> list[list[dict]]:
    sched = []
    for _ in range(n):
        faults = []
        for _ in range(rng.poisson(cfg.faults_per_unit_month * T / 43200)):
            kind = rng.choice(FAULTS, p=[0.30, 0.08, 0.12, 0.10, 0.25, 0.08, 0.07])
            start = int(rng.integers(1440, T - 600))
            if kind == "thermostat_cold":
                dur = int(rng.integers(6 * 60, 30 * 60))
                f = dict(kind=kind, start=start, end=start + dur, setpoint=float(rng.uniform(-4.0, 0.5)),
                         ramp=int(rng.integers(30, 240)))
            elif kind == "relay_stuck_on":
                f = dict(kind=kind, start=start, end=start + int(rng.integers(4 * 60, 16 * 60)))
            elif kind == "compressor_wear":
                f = dict(kind=kind, start=start, end=T, rate=float(rng.uniform(0.02, 0.06)))  # capacity loss per day
            elif kind == "gasket_leak":
                f = dict(kind=kind, start=start, end=T, factor=float(rng.uniform(0.3, 0.6)))
            elif kind == "power_cut":
                f = dict(kind=kind, start=start, end=start + int(rng.integers(30, 14 * 60)))
            elif kind == "sensor_stuck":
                f = dict(kind=kind, start=start, end=start + int(rng.integers(3 * 60, 24 * 60)))
            else:
                f = dict(kind=kind, start=start, end=start + int(rng.integers(12 * 60, 72 * 60)),
                         rate=float(rng.choice([-1, 1]) * rng.uniform(0.5, 2.0)))  # °C drift per day
            faults.append(f)
        sched.append(faults)
    return sched


def simulate_fleet(cfg: FleetConfig = FleetConfig()) -> tuple[pd.DataFrame, pd.DataFrame, list[list[dict]]]:
    """Simulate a fleet.

    Returns (log, units, faults):
      log   – one row per unit per 10-minute logger reading, with the measured air temperature (what eVIN sees)
              and hidden ground truth (true air, true product, compressor, door, power) for labelling only.
      units – one row per unit with its class and parameters.
      faults – per-unit list of injected faults.
    """
    rng = np.random.default_rng(cfg.seed)
    spec = cfg.units_spec
    if spec is not None:
        cfg = FleetConfig(n_units=len(spec), days=cfg.days, seed=cfg.seed, domestic_share=cfg.domestic_share,
                          faults_per_unit_month=cfg.faults_per_unit_month, units_spec=spec)
    n, T = cfg.n_units, cfg.days * 1440
    minutes = np.arange(T)

    cls = np.where(rng.random(n) < cfg.domestic_share, "DOMESTIC", "ILR")
    if spec is not None:
        cls = np.array([u.get("cls", "ILR") for u in spec])
    p = {k: np.array([CLASSES[c][k] for c in cls]) for k in CLASSES["ILR"]}
    for k in p:  # unit-to-unit spread around the class prior
        p[k] = p[k] * rng.lognormal(0.0, 0.15, size=n)
    # Real clinics often run fridges cold: about a quarter sit near the 2 °C edge without any fault
    setpoint0 = np.where(rng.random(n) < 0.25, rng.uniform(2.6, 3.4, size=n), rng.uniform(4.0, 5.5, size=n))
    hyst = rng.uniform(1.6, 2.4, size=n)
    amb_base = rng.uniform(22.0, 36.0, size=n)
    if spec is not None:
        setpoint0 = np.array([u.get("setpoint", 4.8) for u in spec], dtype=float)
        amb_base = np.array([u.get("amb_base", 30.0) for u in spec], dtype=float)

    amb = _ambient(minutes, amb_base, rng)
    door = _doors(n, T, rng)
    faults = _fault_schedule(n, T, cfg, rng) if spec is None else [list(u.get("faults", [])) for u in spec]

    # Per-minute modifiers from faults
    setpoint = np.repeat(setpoint0[:, None], T, axis=1)
    stuck_on = np.zeros((n, T), dtype=bool)
    power = np.ones((n, T), dtype=bool)
    qc_scale = np.ones((n, T))
    rea_scale = np.ones((n, T))
    for i, fl in enumerate(faults):
        for f in fl:
            s, e = f["start"], min(f["end"], T)
            if f["kind"] == "thermostat_cold":
                ramp = np.clip((np.arange(s, e) - s) / f["ramp"], 0, 1)
                setpoint[i, s:e] = setpoint0[i] + ramp * (f["setpoint"] - setpoint0[i])
            elif f["kind"] == "relay_stuck_on":
                stuck_on[i, s:e] = True
            elif f["kind"] == "compressor_wear":
                qc_scale[i, s:e] *= np.clip(1 - f["rate"] * (np.arange(s, e) - s) / 1440, 0.25, 1)
            elif f["kind"] == "gasket_leak":
                rea_scale[i, s:e] *= f["factor"]
            elif f["kind"] == "power_cut":
                power[i, s:e] = False

    Ta = setpoint0 + rng.normal(0, 0.3, n)
    Tp = Ta.copy()
    Te = Ta - 1.0
    comp = np.zeros(n, dtype=bool)
    logged = T // LOG_EVERY
    out = {k: np.zeros((n, logged), dtype=np.float32) for k in ("air", "prod", "amb")}
    out_c = np.zeros((n, logged), dtype=np.float32)   # compressor duty in the interval
    out_d = np.zeros((n, logged), dtype=np.float32)   # door minutes in the interval
    out_p = np.zeros((n, logged), dtype=np.float32)   # powered fraction in the interval
    prod_min = np.zeros((n, T), dtype=np.float32)      # 1-minute true product temperature for labels

    for t in range(T):
        sp = setpoint[:, t]
        comp = np.where(Ta > sp + hyst / 2, True, np.where(Ta < sp - hyst / 2, False, comp))
        u = (comp | stuck_on[:, t]) & power[:, t]
        a = amb[:, t]
        d = door[:, t]
        q_ae = (Te - Ta) / p["R_ae"]
        q_ap = (Tp - Ta) / p["R_ap"]
        q_door = d * (a - Ta) / p["R_door"]
        q_ea = (a - Te) / (p["R_ea"] * rea_scale[:, t])
        Ta = Ta + DT * (q_ae + q_ap + q_door) / p["C_a"]
        Tp = Tp + DT * (-q_ap) / p["C_p"]
        Te = Te + DT * (q_ea - q_ae - u * p["Q_c"] * qc_scale[:, t]) / p["C_e"]
        prod_min[:, t] = Tp
        k = t // LOG_EVERY
        out_c[:, k] += u
        out_d[:, k] += d
        out_p[:, k] += power[:, t]
        if t % LOG_EVERY == LOG_EVERY - 1:
            out["air"][:, k] = Ta
            out["prod"][:, k] = Tp
            out["amb"][:, k] = a

    # What the logger reports: noise, 0.1 °C resolution, plus sensor faults and occasional dropouts
    meas = out["air"] + rng.normal(0, 0.08, size=out["air"].shape)
    for i, fl in enumerate(faults):
        for f in fl:
            s, e = f["start"] // LOG_EVERY, min(f["end"], T) // LOG_EVERY
            if f["kind"] == "sensor_stuck" and e > s:
                meas[i, s:e] = meas[i, s]
            elif f["kind"] == "sensor_drift" and e > s:
                meas[i, s:e] += f["rate"] * np.arange(e - s) * LOG_EVERY / 1440
    meas = np.round(meas, 1)
    meas[rng.random(meas.shape) < 0.003] = np.nan

    tick = np.arange(logged)
    log = pd.DataFrame({
        "unit": np.repeat(np.arange(n), logged),
        "tick": np.tile(tick, n),
        "minute": np.tile((tick + 1) * LOG_EVERY, n),
        "air_meas": meas.ravel(),
        "air_true": out["air"].ravel(),
        "prod_true": out["prod"].ravel(),
        "ambient": out["amb"].ravel(),
        "duty": (out_c / LOG_EVERY).ravel(),
        "door_min": out_d.ravel(),
        "powered": (out_p / LOG_EVERY).ravel(),
    })
    units = pd.DataFrame({"unit": np.arange(n), "cls": cls, "setpoint": setpoint0, "amb_base": amb_base,
                          **{k: v for k, v in p.items()}})
    units["tau_prod_min"] = units["C_p"] * units["R_ap"] / 60.0
    log.attrs["prod_min"] = prod_min
    return log, units, faults
