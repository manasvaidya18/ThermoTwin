# ThermoTwin · Team Alebaple · CODE APEX 3.0 (Track 4, T4-1)

AI predictive early warning for vaccine cold-chain fridges, from temperature readings alone (what eVIN loggers record).
A digital twin estimates the vaccine's own temperature (the **Virtual Vial**); calibrated LightGBM hazard models warn
before the vaccine freezes or overheats, name the likely cause and say what to do. Results so far are on simulated
fridges (ColdChain Gym), not field data.

## Repository layout

```
.
├── frontend/                 Phone app (clinic staff) + website (district officer); static, works offline
│   ├── mobile/  web/  shared/
│   ├── index.html  phone.html  serve.py  START_DEMO.bat  START_LIVE.bat
│   └── design/               original Stitch exports (reference only)
├── backend/                  Microservices (FastAPI)
│   ├── common/               config, database access, HTTP client, clock labels
│   ├── services/
│   │   ├── gateway/          public /api/* + serves the frontend          :8080
│   │   ├── telemetry/        fridge registry, readings, demo clock        :8101
│   │   ├── inference/        digital twin + risk + cause models           :8102
│   │   └── alerts/           Guardian tiers, Cause Cards, vaccine-aware   :8103
│   ├── tests/
│   ├── run_all.py            all services in one process (demo)
│   └── run_services.py       each service as its own process
├── ml/                       Models and research code
│   ├── thermotwin/           simulator, twin, features, labels, hazard model, cause model, benchmark, LSTM baseline
│   ├── scripts/              train.py, run_baselines.py, tradeoff.py
│   ├── artifacts/            trained models (models.pkl)
│   ├── results/              benchmark CSVs, summaries, logs
│   └── tests/
├── db/                       schema.sql, seed/ data, init_db.py (SQLite, created on first start)
├── scripts/                  Windows one-click launchers
└── docs/                     PRD, status report, research, planning, pitch-deck assets
```

## How the services fit together

```
frontend ──HTTP──> gateway ──> telemetry  (registry, readings, clock)  ──> db: fridges, stock, readings
                       └─────> alerts ──> telemetry (readings)
                                     └──> inference (twin + models)   ──> ml/artifacts/models.pkl
                                     └──> db: vaccines, alert_events
```

Each service is a plain Python class (`service.py`) with a thin FastAPI wrapper (`app.py`). The gateway reaches the
others in one of two modes, with identical output:

- `TT_MODE=local` (default): everything in one process on one port. Use this for the demo.
- `TT_MODE=http`: each service is its own process, talking over HTTP.

## Quick start

```bash
pip install -r backend/requirements.txt        # also installs ml/requirements.txt

python backend/run_all.py                      # demo: http://localhost:8080
python backend/run_services.py                 # microservices: 4 processes

python -m pytest -q ml/tests backend/tests     # tests
python ml/scripts/train.py                     # retrain models (about 1 min)
```

On Windows you can use the launchers in `scripts/` instead. For the offline UI with fixed demo data, open
`frontend/index.html` or run `python frontend/serve.py 8080`.

## API (gateway)

| Method | Path | Returns |
|---|---|---|
| GET | `/api/state` | demo clock |
| POST | `/api/clock` `{action: play\|pause\|reset\|step, ticks}` | demo clock |
| GET | `/api/fridges` | every fridge: tier, Virtual Vial, risk, time to breach, cause, stock, door-recovery note, cooling health and days until service |
| GET | `/api/fridges/{id}?hours=24` | one fridge with history, forecast and 24 h exposure |
| GET | `/api/alerts` | fridges not in Normal |
| GET | `/api/alerts/history?fridge_id=` | tier changes so far (from the database) |
| GET | `/api/health` | status of the services |

## Results (simulated, held-out fridges)

Freeze: 41/41 caught, about 100 min warning before the vaccine reaches 0 °C, 0.45 false alerts per fridge-month
(WHO rule: 30 min *after*). Details, the LSTM comparison and the heat results are in [ml/README.md](ml/README.md).
