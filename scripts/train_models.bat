@echo off
rem Retrain freeze, heat and cause models, then the slow-loop degradation model -> prediction_engine\models\models.pkl
cd /d "%~dp0.."
python prediction_engine\training\scripts\train.py
python prediction_engine\training\scripts\train_degradation.py
