@echo off
title Lyra Core Setup
echo ========================================================
echo               LYRA V1 CORE INSTALLER SEQUENCE           
echo ========================================================
echo.
echo [1/3] Building python private server...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo.
echo [2/3] Downloading user interface packages...
cd frontend
call npm install
cd ..

echo.
echo ========================================================
echo [OK] Lyra V1 Core Setup complete. Run "npm run dev" to start.
echo ========================================================
pause
