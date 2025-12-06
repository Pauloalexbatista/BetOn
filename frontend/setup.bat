@echo off
echo ========================================
echo   BetOn Frontend - First Time Setup
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ first
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found!
    echo Please install Node.js 18+ first
    pause
    exit /b 1
)

echo [1/1] Installing dependencies...
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure backend is running (backend\start.bat)
echo 2. Run start.bat to start the frontend
echo.
pause
