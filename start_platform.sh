#!/usr/bin/env bash
# ===============================================================================
#        AMAZON-AI RETAIL INTELLIGENCE PLATFORM - LAUNCHER
# ===============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==============================================================================="
echo "       AMAZON-AI RETAIL INTELLIGENCE PLATFORM - LAUNCHER"
echo "==============================================================================="
echo ""
echo "[1/2] Launching FastAPI MLOps Backend Server (Port 8000)..."
(cd "$PROJECT_DIR/backend" && "$PROJECT_DIR/venv_linux/bin/python3" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

echo "[2/2] Launching Next.js 16 Frontend App (Port 3000)..."
(cd "$PROJECT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "==============================================================================="
echo " SERVICES ARE LAUNCHING IN THE BACKGROUND!"
echo "==============================================================================="
echo ""
echo "  -> Frontend Web Application : http://localhost:3000"
echo "  -> Backend API Swagger Docs : http://localhost:8000/docs"
echo "  -> Backend Root Status      : http://localhost:8000/"
echo ""
echo "Press Ctrl+C to terminate both services."
echo "==============================================================================="

trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM EXIT
wait
