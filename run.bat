@echo off
REM Setup virtual environment if it does not exist
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
