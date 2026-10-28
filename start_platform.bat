@echo off
title Amazon-AI Retail Intelligence Platform - Launcher
echo ===============================================================================
echo        AMAZON-AI RETAIL INTELLIGENCE PLATFORM - LAUNCHER
echo ===============================================================================
echo.
echo [1/2] Launching FastAPI MLOps Backend Server (Port 8000)...
start "Amazon-AI Backend (Port 8000)" cmd /k "cd /d "%~dp0" && backend\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Next.js 15 Frontend E-Commerce App (Port 3000)...
start "Amazon-AI Frontend (Port 3000)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===============================================================================
echo  SERVICES ARE LAUNCHING IN TWO SEPARATE WINDOWS!
echo ===============================================================================
echo.
echo   -> Frontend Web Application : http://localhost:3000
echo   -> Backend API Swagger Docs : http://localhost:8000/docs
echo   -> MLOps Model Status API   : http://localhost:8000/model/status
echo.
echo Keep both command windows open while using the application.
echo ===============================================================================
echo.
