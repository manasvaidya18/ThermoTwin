# Workers

Background jobs. Each loads Django from `backend/` and uses the same services as the API.

| Worker | Does | Schedule |
|---|---|---|
| `telemetry_worker.py` | builds the demo readings, or imports a logger / eVIN CSV (`unit,timestamp,temp_c`) as live readings | on demand |
| `prediction_worker.py` | scores every unit with live readings and records alert events | every 10 min (`--interval 600`) |
| `escalation_worker.py` | raises unacknowledged Critical / Early warning alerts to the officer, then the senior officer (simulated SMS) | every minute (`--interval 60`) |
| `maintenance_worker.py` | opens maintenance tickets for units whose cooling is weakening, assigned to the saved technician | daily |
