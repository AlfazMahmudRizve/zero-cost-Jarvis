@echo off
set PYTHONIOENCODING=utf-8
if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found using .venv\Scripts\python.exe
    echo Please run setup_jarvis.bat first.
    pause
    exit /b 1
)

echo [JARVIS] Launching...
.venv\Scripts\python.exe main.py
if %errorlevel% neq 0 pause
