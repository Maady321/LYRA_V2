@echo off
title Lyra Core Launcher
echo ========================================================
echo               LYRA V1 CORE LAUNCH SEQUENCE              
echo ========================================================
echo [1/3] Spinning up Private FastAPI orchestrator...
start "Lyra Core Backend Server" cmd /k "cd backend && venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Launching Vite compiler server...
start "Lyra Core Frontend Compiler" cmd /k "cd frontend && npm run dev"

echo [3/3] Synchronizing network sockets...
timeout /t 5 /nobreak > NUL

echo ========================================================
echo [OK] Lyra Services connected. Booting Electron Desktop UI.
echo ========================================================
cd frontend && npm run electron
