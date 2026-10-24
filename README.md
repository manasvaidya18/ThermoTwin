# ThermoTwin · Team Alebaple · CODE APEX 3.0 (Track 4, T4-1)

AI predictive early warning for cold-chain networks (government vaccine stores down to PHC fridges, and private
cold-storage operators), from temperature readings alone (what eVIN loggers already record). A digital twin estimates
the vaccine's own temperature (the **Virtual Vial**); LightGBM models warn before it freezes or overheats, name the
likely cause and say why; a daily slow loop predicts how many days remain before a unit needs service.

## Repository layout

```
thermotwin/
├── backend/                 Django + Django REST Framework (users, network, readings, alerts, incidents, reports)
│   ├── config/              settings, urls, asgi, wsgi, middleware, frontend serving
│   ├── apps/
│   │   ├── accounts/        login (token), roles: officer / employee / technician / driver / admin
│   │   ├── organizations/   government departments and private firms
│   │   ├── facilities/      facilities, storage units, vaccines, stock, technicians (+ seed_demo command)
│   │   ├── telemetry/       readings, devices (ESP32 / eVIN), demo scenario and clock
│   │   ├── alerts/          alert levels (Guardian tiers), events, acknowledgements, escalation, prediction client
│   │   ├── incidents/       corrective actions and maintenance tickets
│   │   └── reports/         summary, alert and incident exports
│   └── manage.py
├── prediction_engine/       independent FastAPI ML service
│   ├── app/                 main.py (FastAPI), config.py, schemas.py
│   ├── services/            prediction, risk (freeze/heat/cause), explanation (SHAP), recovery, maintenance, model loader
│   ├── digital_twin/        virtual_vial.py (Kalman filter), thermal_model.py (3-node RC fridge physics simulator)
│   ├── ingestion/           data_validator.py (reading checks + trust check), preprocessing.py (features)
│   ├── models/              models.pkl (trained models + thresholds)
│   ├── training/            labels, benchmark, pipeline, LSTM baseline, datasets, scripts/
│   ├── results/             benchmark and real-data validation results
│   └── tests/
├── workers/                 telemetry, prediction, escalation and maintenance jobs
├── frontend/                website (officers) + phone app (site staff): HTML/JS, works offline and live
├── shared/schemas/          JSON Schemas for readings, scored readings and fridge summaries
├── tests/                   end-to-end API tests (Django)
├── scripts/                 run_demo.py and Windows launchers
├── docs/                    PRD, status report, research, planning, pitch assets
├── .env.example
└── README.md
```

## How the parts talk

```
devices (ESP32 / eVIN) ──POST /api/readings──▶ Django backend ──POST /score──▶ prediction engine (FastAPI)
website + phone app  ◀──────── /api/* ──────── (alerts, incidents,  ◀── scored readings: Virtual Vial, risk,
                                                 reports, workers)        countdown, cause, reasons, health
```

Django handles users, the network, readings, alerts and tickets. The ML runs in the FastAPI prediction engine; if it is
not running, Django runs the same engine in-process so the demo still works.

## Run

```bash
pip install -r backend/requirements.txt          # also installs prediction_engine/requirements.txt
cp .env.example .env                             # optional: set passwords and keys
python scripts/run_demo.py                       # migrate + seed + engine (:8102) + Django (:8080)
```

Open http://localhost:8080 (website and phone app; the LIVE MODEL bar drives the demo clock). On Windows,
`scripts/start_demo_live.bat` does the same. For the frontend alone with fixed data: `python frontend/serve.py 8080`.

Demo users (created by `seed_demo`, password from `TT_DEMO_PASSWORD`): `officer`, `wagholi_staff`, `technician`, `driver`.

```bash
python -m pytest -q prediction_engine/tests      # engine tests
python backend/manage.py test tests              # end-to-end API tests
```

## API (backend)

| Method | Path | What |
|---|---|---|
| GET | `/api/state`, POST `/api/clock` | demo clock (play, pause, step, reset) |
| GET | `/api/fridges`, `/api/fridges/<id>` | every unit: alert level, Virtual Vial, risk, countdown, cause, reasons, recovery note, cooling health, technicians |
| GET | `/api/alerts`, `/api/alerts/history` | active alerts; tier changes |
| POST | `/api/alerts/<id>/acknowledge` | staff acknowledge (stops escalation) |
| POST | `/api/readings` | device readings (`X-Device-Key`) or staff upload |
| GET | `/api/units/<id>/live` | latest status from a unit's live readings |
| POST | `/api/auth/login`, GET `/api/auth/me`, POST `/api/auth/register` | token login, roles |
| CRUD | `/api/organizations`, `/api/facilities`, `/api/units`, `/api/vaccines`, `/api/stock`, `/api/technicians` | network setup (officers) |
| CRUD | `/api/incidents`, POST `/api/incidents/<id>/actions`, `/resolve` | corrective actions, maintenance tickets |
| GET | `/api/reports/summary`, `/api/reports/alerts.csv`, `/api/reports/incidents.csv` | reports and exports |
| GET | `/api/health` | backend and prediction-engine status |

Prediction engine: `GET /health`, `GET /info`, `POST /score`, `POST /validate` (see `shared/schemas/`).

## Workers

```bash
python workers/telemetry_worker.py [--csv export.csv]     # demo readings, or import a logger / eVIN CSV
python workers/prediction_worker.py [--interval 600]      # score units with live readings
python workers/escalation_worker.py [--interval 60]       # escalate unacknowledged alerts (simulated SMS)
python workers/maintenance_worker.py                      # daily: open maintenance tickets from the slow loop
```

## Results

Simulated, held-out fridges: 41/41 freezes caught about 100 min before the vaccine reaches 0 °C, 0.45 false alerts per
fridge-month (WHO alarm: 30 min after); 99.1% of normal door openings raise no alert; 22/30 gradual failures flagged a
median 7 days early. Real data: the Virtual Vial on 123 Bangkok fridges (median error 0.28 °C after one-day
calibration) and 17/23 real service-dated freezer faults flagged in the 14 days before service. Details:
[prediction_engine/README.md](prediction_engine/README.md).
