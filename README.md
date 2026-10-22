# ThermoTwin · Team Alebaple · CODE APEX 3.0 (Track 4, T4-1)

AI predictive early warning for vaccine cold-chain fridges. It works from temperature readings alone (what eVIN loggers record).
A digital twin estimates the vaccine's own temperature (the "Virtual Vial"). A calibrated LightGBM hazard model warns about
100 minutes before the vaccine reaches 0 °C, with under 0.5 false alerts per fridge-month (simulated, held-out fridges).

## Repository layout

| Folder | What's inside |
|---|---|
| `thermotwin/` | Core system: simulator, twin, risk and cause models, benchmark, LSTM baseline, live API. See `thermotwin/README.md`. |
| `ui/app/` | Phone app (clinic staff) and website (district officer). Static, works offline; goes live with the API. |
| `ui/dashboard`, `ui/monitor` | Original Stitch UI exports (reference) |
| `ppt_assets/` | Scripts and images for the pitch-deck charts and diagrams |
| `reports/`, `research_notes/` | Market research and the status/plan report |
| `thermotwin_blueprint/`, `pitch_playbook/`, `CodeApex_Analysis.md` | Early problem analysis and planning |
| `ThermoTwin_PRD.docx`, `ThermoTwin_status_and_plan.pdf` | PRD and status report |

## Quick start

```bash
cd thermotwin
pip install -r requirements.txt
python run_core_path.py      # train + benchmark (about 1 min), writes outputs/
python serve_live.py         # http://localhost:8080 : live UI + API
python -m pytest -q          # tests
```

Offline UI only: open `ui/app/index.html`, or run `python ui/app/serve.py 8080`.

All results are on simulated fridges, not field data.
