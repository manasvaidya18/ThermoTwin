@echo off
cd /d "%~dp0"
echo ThermoTwin LIVE demo (real model) at http://localhost:8080  (close this window to stop)
echo First start takes about 15 seconds while the models score the demo fridges.
start "" http://localhost:8080
python "%~dp0..\backend\run_all.py" 8080
