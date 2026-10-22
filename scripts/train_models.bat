@echo off
rem Retrain freeze, heat and cause models -> ml\artifacts\models.pkl, results in ml\results
cd /d "%~dp0..\ml"
python scripts\train.py
