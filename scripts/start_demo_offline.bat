@echo off
rem Frontend only, fixed demo data, no Python packages needed
cd /d "%~dp0..\frontend"
start "" http://localhost:8080
python serve.py 8080
