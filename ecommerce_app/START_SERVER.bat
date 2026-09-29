@echo off
echo ============================================
echo   SmartRec Server - Starting...
echo ============================================
cd /d "d:\3rd sem created files\AIML PROJECT\ecommerce_app"

:: Kill any old processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Starting server on http://127.0.0.1:8000
echo Press CTRL+C to stop.
echo.

.\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
