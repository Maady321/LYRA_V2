@echo off
title Lyra Core Launcher
color 0B
cls

echo ========================================================
echo               LYRA V1 CORE AUTOMATED LAUNCHER            
echo ========================================================
echo.

:: 1. Detect Node.js installation
echo [INFO] Detecting Node.js environment...
where node >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Node.js is NOT installed on this system!
    echo.
    echo Lyra's desktop user interface requires Node.js to be compiled.
    echo Please download and install Node.js from: https://nodejs.org/
    echo *Select the LTS - Long Term Support - version.*
    echo.
    pause
    exit /b
)
echo [OK] Node.js environment detected.

:: 2. Detect Python environment
echo [INFO] Detecting Python environment...
where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is NOT installed on this system!
    echo.
    echo Lyra's local backend services require Python 3.10 or higher.
    echo Please download and install Python from: https://www.python.org/
    echo *CRITICAL: Make sure to check "Add Python to PATH" during installation.*
    echo.
    pause
    exit /b
)
echo [OK] Python environment detected.

:: 3. Check and run installation if needed
set FIRST_RUN=0
if not exist "backend\venv" (
    set FIRST_RUN=1
)
if not exist "frontend\node_modules" (
    set FIRST_RUN=1
)

if %FIRST_RUN% equ 1 (
    echo [INFO] First-time setup detected. Initializing installation sequence...
    echo [INFO] This will build the Python virtual environment and download packages.
    echo.
    call scripts\setup.bat
)

:: 4. Start Lyra Core Platform
echo.
echo ========================================================
echo [OK] All system checks passed. Booting Lyra Core...
echo ========================================================
echo.
call npm run dev
