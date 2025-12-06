@echo off
echo ========================================
echo   BetOn - Starting All Services
echo ========================================
echo.

REM Start Backend in new window
echo Starting Backend...
start "BetOn Backend" cmd /k "cd backend && start.bat"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo Starting Frontend...
start "BetOn Frontend" cmd /k "cd frontend && start.bat"

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Check the opened windows for logs
echo.
pause
