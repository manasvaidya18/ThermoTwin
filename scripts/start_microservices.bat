@echo off
rem Each service as its own process: telemetry 8101, inference 8102, alerts 8103, gateway 8080
cd /d "%~dp0.."
python backend\run_services.py
