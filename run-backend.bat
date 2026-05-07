@echo off
cd /d "%~dp0backend"
if not exist venv (
  python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
