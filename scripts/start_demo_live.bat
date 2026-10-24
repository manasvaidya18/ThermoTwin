@echo off
rem ThermoTwin: Django backend + FastAPI prediction engine + website/phone app on http://localhost:8080
cd /d "%~dp0.."
start "" http://localhost:8080
python scripts\run_demo.py 8080
