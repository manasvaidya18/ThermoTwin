@echo off
rem Live demo: all backend services in one process + frontend on http://localhost:8080
cd /d "%~dp0.."
start "" http://localhost:8080
python backend\run_all.py 8080
