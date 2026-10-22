import pytest

from backend.common import config


@pytest.fixture(scope="module")
def client():
    if not config.MODELS_PATH.exists():
        pytest.skip("train the models first: python ml/scripts/train.py")
    from fastapi.testclient import TestClient
    from backend.services.gateway.app import app
    c = TestClient(app)
    c.post("/api/clock", json={"action": "reset"})
    yield c
    c.post("/api/clock", json={"action": "reset"})


def test_gateway_tells_the_wagholi_story(client):
    """End to end: DB readings -> inference (twin + models) -> alerts (Guardian tiers) -> gateway JSON."""
    client.post("/api/clock", json={"action": "reset"})
    tiers = []
    for _ in range(12):
        tiers.append(client.get("/api/fridges/wagholi-ilr1").json()["tier"])
        client.post("/api/clock", json={"action": "step", "ticks": 6})
    assert "Early warning" in tiers and "Critical" in tiers
    assert tiers.index("Early warning") < tiers.index("Critical")
    d = client.get("/api/fridges/wagholi-ilr1").json()
    assert d["cause"]["key"] == "cooling_too_hard" and len(d["series"]["air"]) > 100
    assert d["stock_note"] == "" or d["stock_note"].startswith("Protect first")


def test_alert_history_comes_from_the_database(client):
    client.post("/api/clock", json={"action": "step", "ticks": 200})
    ev = client.get("/api/alerts/history", params={"fridge_id": "wagholi-ilr1"}).json()["events"]
    assert [e["tier"] for e in ev][:2] == ["Critical", "Early warning"]


def test_unknown_fridge_and_bad_clock_action(client):
    assert client.get("/api/fridges/nope").status_code == 404
    assert client.post("/api/clock", json={"action": "jump"}).status_code == 400


def test_health(client):
    h = client.get("/api/health").json()
    assert h["gateway"]["ok"] and h["telemetry"]["ok"] and h["alerts"]["ok"]


def test_vaccine_aware_downgrade():
    from backend.services.alerts.vaccines import adjust_tier
    cat = {"Pentavalent": True, "OPV": False, "MR": False}
    assert adjust_tier("Early warning", "freeze", ["OPV", "MR"], cat)[0] == "Advisory"
    assert adjust_tier("Early warning", "freeze", ["Pentavalent", "OPV"], cat) == ("Early warning", "Protect first: Pentavalent")
    assert adjust_tier("Critical", "freeze", ["OPV"], cat)[0] == "Critical"        # measured breaches never downgraded
    assert adjust_tier("Early warning", "heat", ["OPV"], cat)[0] == "Early warning"
    assert adjust_tier("Early warning", "freeze", ["NewVaccine"], cat)[0] == "Early warning"  # unknown = sensitive
