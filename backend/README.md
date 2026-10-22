# Backend services

| Service | Folder | Port | Owns | Calls |
|---|---|---|---|---|
| gateway | `services/gateway` | 8080 | public `/api/*`, serves `frontend/` | telemetry, alerts |
| telemetry | `services/telemetry` | 8101 | fridge registry, readings, demo clock (tables `facilities`, `fridges`, `fridge_stock`, `readings`) | none |
| inference | `services/inference` | 8102 | loaded models (`ml/artifacts/models.pkl`); stateless | none |
| alerts | `services/alerts` | 8103 | Guardian tiers, Cause Cards, vaccine-aware alerts (table `alert_events`) | telemetry, inference |

Each service has `service.py` (logic, plain Python) and `app.py` (FastAPI routes). `common/` holds the settings
(`config.py`, all overridable by environment variables), database access (`db.py`), the HTTP client (`http.py`)
and clock labels.

## Service APIs

- **telemetry:** `GET /health`, `GET /fridges`, `GET /readings`, `GET /clock`, `POST /clock`
- **inference:** `GET /health`, `GET /info`, `POST /score {fridges, readings}` returns one scored row per reading
- **alerts:** `GET /health`, `GET /fleet?tick=`, `GET /fridges/{id}?tick=&hours=`, `GET /fridges/{id}/summary?tick=`, `GET /history?tick=&fridge_id=`
- **gateway:** see the root README

## Run

```bash
python backend/run_all.py          # one process (TT_MODE=local), port 8080
python backend/run_services.py     # four processes (TT_MODE=http)
python -m pytest -q backend/tests
```

## Environment variables

| Variable | Default |
|---|---|
| `TT_MODE` | `local` (or `http`) |
| `TT_DB` | `db/thermotwin.db` |
| `TT_MODELS` | `ml/artifacts/models.pkl` |
| `TT_SCENARIO` | `services/telemetry/scenarios/pune_demo.json` |
| `TT_FRONTEND` | `frontend/` |
| `TT_TELEMETRY_URL`, `TT_INFERENCE_URL`, `TT_ALERTS_URL` | `http://127.0.0.1:8101` / `8102` / `8103` |

## Demo scenario

`services/telemetry/scenarios/pune_demo.json` scripts six Pune fridges over 3 days. On first start, telemetry
simulates them and stores the readings in the database:
- PHC Wagholi ILR-1 drifts cold: Advisory, then Early warning, then Critical.
- Junnar has a power cut.
- Baramati has weak cooling.
- Khed has a stuck probe.
- Shirur runs cold.
- Lonikand is healthy.

Facility names and vaccine stock come from `db/seed/`.
