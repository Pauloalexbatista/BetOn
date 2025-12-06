@echo off
echo ========================================
echo   BetOn Frontend - Starting...
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules\" (
    echo [ERROR] Dependencies not installed!
    echo Please run setup_frontend.bat first
    pause
    exit /b 1
)

REM Start Next.js development server
echo [1/1] Starting Next.js development server...
echo.
echo ========================================
echo   Frontend running at:
echo   - App: http://localhost:3000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
