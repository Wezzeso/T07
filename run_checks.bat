@echo off
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python -m experiments.run_all
if errorlevel 1 exit /b 1
.venv\Scripts\python -m pytest -q --disable-warnings
pause
