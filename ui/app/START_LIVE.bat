@echo off
cd /d "%~dp0"
echo ThermoTwin LIVE demo (real model) at http://localhost:8080  (close this window to stop)
echo First start takes about 10 seconds while the model scores the demo fridges.
start "" http://localhost:8080
python "%~dp0..\..\thermotwin\serve_live.py" 8080
