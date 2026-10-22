ThermoTwin UI demo
==================

Windows: double-click START_DEMO.bat. The browser opens http://localhost:8080.
Mac/Linux: open a terminal in this folder and run:  python3 serve.py 8080
Then open http://localhost:8080. Python 3 is the only requirement. Everything works offline.
Live model instead of fixed data: START_LIVE.bat (needs pip install -r ../backend/requirements.txt).

Phone app (clinic handler)  ->  phone.html
  Home > tap ILR-1 > Cause Card > "I've done this"
  Bottom tabs: Home, Alerts (filters), Help.  EN / हिं toggle top right.

Website (district officer)  ->  web/overview.html
  Sidebar: Overview, Facilities, Alerts, Maintenance, Exposure Ledger, Benchmark, Settings, Ask ThermoTwin
  Top bar: Emergency SOP checklist, SMS broadcast, Export report
  Click "PHC Wagholi" anywhere to open the ILR-1 digital twin (chart layers, Simulate a scenario,
  Lifeboat routing, twin health, maintenance confirm, exposure ledger).

Clickable mock-up with fixed demo data; actions show a "Demo:" message instead of sending anything.
If you opened an older version before, press Ctrl+F5 once.
