# Backend (Django + Django REST Framework)

Application data in **PostgreSQL**; sensor readings and model outputs in **InfluxDB** (`apps/telemetry/timeseries.py`,
with a PostgreSQL table as fallback). Settings come from `.env`.

```bash
python backend/manage.py migrate
python backend/manage.py seed_demo          # Pune demo network + demo users
python backend/manage.py runserver 8080     # or: python scripts/run_demo.py (also starts the prediction engine)
python backend/manage.py test tests         # from the repo root
python backend/manage.py createsuperuser    # Django admin at /admin/
```

| App | Models | Endpoints |
|---|---|---|
| `accounts` | `Profile` (role: admin, officer, employee, technician, driver; organization; facilities) | `/api/auth/login`, `/logout`, `/me`, `/register` |
| `organizations` | `Organization` (government / private) | `/api/organizations` |
| `facilities` | `Facility`, `StorageUnit`, `Vaccine`, `StockItem`, `Technician` | `/api/facilities`, `/api/units`, `/api/vaccines`, `/api/stock`, `/api/technicians` |
| `telemetry` | `Device` (hashed key); readings in InfluxDB (`timeseries.py`), with `Reading` as the PostgreSQL fallback | `/api/state`, `/api/clock`, `/api/readings` |
| `alerts` | `AlertEvent` (tier changes, escalation level), `Acknowledgement` | `/api/fridges`, `/api/fridges/<id>`, `/api/alerts`, `/api/alerts/history`, `/api/alerts/<id>/acknowledge`, `/api/units/<id>/live`, `/api/health` |
| `incidents` | `Incident`, `IncidentAction` | `/api/incidents`, `/api/incidents/<id>/actions`, `/resolve` |
| `reports` | (none) | `/api/reports/summary`, `/alerts.csv`, `/incidents.csv` |

Each app has `models.py`, `serializers.py`, `views.py`, `services.py` (the logic) and `urls.py`. Alert rules live in
`apps/alerts/rules.py` and `vaccines.py`; `apps/alerts/prediction_client.py` calls the prediction engine at
`TT_ENGINE_URL`, or runs it in-process if it is not reachable.

Permissions: reading dashboards is open (demo); changing network setup needs an officer; acknowledging alerts and
working incidents needs any logged-in user; devices post readings with their own key (`X-Device-Key`).
