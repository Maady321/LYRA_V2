@echo off
title MJ AI Assistant Launcher
color 0A
cls

echo ========================================================
echo               MJ MULTI-AGENT AI SYSTEM BOOT             
echo ========================================================
echo.

if not exist "venv" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please make sure dependencies are fully installed first.
    echo.
    pause
    exit /b
)

echo [OK] Activating environment...
call venv\Scripts\activate.bat

echo [OK] Launching MJ Platform console...
venv\Scripts\python.exe main.py

pause
