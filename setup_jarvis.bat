@echo off
echo [JARVIS] Setting up environment...

if not exist .venv (
    echo [JARVIS] Creating virtual environment...
    python -m venv .venv
)

echo [JARVIS] Activating venv...
call .venv\Scripts\activate.bat

echo [JARVIS] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [JARVIS] Setup complete.
exit /b 0
