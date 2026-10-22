import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

from thermotwin.benchmark import _consecutive, run_benchmark  # noqa: E402
from thermotwin.labels import find_events  # noqa: E402
from thermotwin.simulator import FleetConfig, simulate_fleet  # noqa: E402
from thermotwin.twin import run_twin  # noqa: E402


def test_virtual_vial_ignores_door_spike():
    air = np.full((1, 30), 4.0)
    air[0, 10] = 11.0                      # one reading after a door opening
    vial = run_twin(air, np.array([60.0]))["vial"][0]
    assert vial.max() - 4.0 < 1.5          # the vial estimate barely moves
    assert abs(vial[-1] - 4.0) < 0.3


def test_virtual_vial_follows_a_real_drop():
    air = np.concatenate([np.full(12, 4.0), np.linspace(4.0, -1.0, 24)])[None, :]
    vial = run_twin(air, np.array([60.0]))["vial"][0]
    assert vial[-1] < 1.0                  # follows the trend
    assert vial[-1] > air[0, -1]           # but lags the air


def test_freeze_event_definition():
    prod = np.full((1, 400), 3.0)
    prod[0, 100:130] = -1.0                # 30 min below -0.5: not an event
    prod[0, 200:290] = -1.0                # 90 min: an event
    ev = find_events(prod, "freeze")
    assert len(ev) == 1 and ev.iloc[0].onset_min == 200


def test_consecutive_rule():
    m = np.array([[1, 1, 0, 1, 1, 1]], dtype=bool)
    assert _consecutive(m, 3).tolist() == [[False, False, False, False, False, True]]


def test_healthy_fleet_stays_in_range():
    log, units, _ = simulate_fleet(FleetConfig(n_units=20, days=3, seed=3, faults_per_unit_month=0))
    assert (log["prod_true"] <= -0.5).mean() == 0
    assert (log["prod_true"] > 8).mean() < 0.01


def test_benchmark_runs():
    log, units, _ = simulate_fleet(FleetConfig(n_units=10, days=3, seed=4))
    air = log.sort_values(["unit", "tick"])["air_meas"].to_numpy().reshape(10, -1)
    ev = find_events(log.attrs["prod_min"], "freeze")
    res = run_benchmark(air, ev, None, 0.5, 3)
    assert set(res["policy"]).issuperset({"P1 WHO (<= -0.5 °C for 60 min)"})


def test_repeat_alerts_count_once():
    from thermotwin.benchmark import episodes
    a = np.zeros((1, 100), dtype=bool)
    a[0, [10, 11, 20, 21, 80]] = True      # flicker at 10 and 20 is one incident; 80 is a new one
    assert episodes(a) == [(0, 10), (0, 80)]


def test_live_api_tells_the_wagholi_story():
    """End to end: scripted fridge -> twin -> trained models -> Guardian tiers -> JSON API."""
    import pathlib
    import pytest
    if not (pathlib.Path(__file__).parents[1] / "outputs" / "models.pkl").exists():
        pytest.skip("run run_core_path.py first to train the models")
    from fastapi.testclient import TestClient
    from thermotwin.api import app, engine
    c = TestClient(app)
    c.post("/api/clock", json={"action": "reset"})
    tiers = []
    for _ in range(12):
        tiers.append(c.get("/api/fridges/wagholi-ilr1").json()["tier"])
        c.post("/api/clock", json={"action": "step", "ticks": 6})
    assert "Early warning" in tiers and "Critical" in tiers
    assert tiers.index("Early warning") < tiers.index("Critical")
    d = c.get("/api/fridges/wagholi-ilr1").json()
    assert d["cause"]["key"] == "cooling_too_hard" and len(d["series"]["air"]) > 100
    c.post("/api/clock", json={"action": "reset"})


def test_vaccine_aware_downgrade():
    from thermotwin.vaccines import adjust_tier
    assert adjust_tier("Early warning", "freeze", ["OPV", "MR"])[0] == "Advisory"
    assert adjust_tier("Early warning", "freeze", ["Pentavalent", "OPV"]) == ("Early warning", "Protect first: Pentavalent")
    assert adjust_tier("Critical", "freeze", ["OPV"])[0] == "Critical"       # measured breaches never downgraded
    assert adjust_tier("Early warning", "heat", ["OPV"])[0] == "Early warning"
