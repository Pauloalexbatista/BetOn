@echo off
title BetOn Launcher
cls
echo ==================================================
echo         PRJT BetOn - Betting Automation
echo ==================================================
echo.
echo [1/3] Starting Backend Server...
start "BetOn Backend" cmd /k "cd backend && start.bat"

echo.
echo [2/3] Starting Frontend Server...
start "BetOn Frontend" cmd /k "cd frontend && start.bat"

echo.
echo [3/3] Waiting for servers to warmup...
timeout /t 10 /nobreak >nul

echo.
echo [>>] Opening Dashboard in your browser...
start http://localhost:3000

echo.
echo ==================================================
echo    SYSTEM IS RUNNING! (Keep windows open)
echo ==================================================
echo.
echo Dashboard: http://localhost:3000
echo API Docs:  http://localhost:8000/docs
echo.
echo To stop: Close the black server windows.
echo.
pause
