@echo off
cd /d "%~dp0.."
python -m pytest -q prediction_engine\tests
python backend\manage.py test tests
