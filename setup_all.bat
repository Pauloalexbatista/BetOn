@echo off
echo ========================================
echo   BetOn - Complete Setup
echo ========================================
echo.
echo This will setup both backend and frontend
echo.
pause

REM Setup Backend
echo.
echo ========================================
echo   Setting up Backend...
echo ========================================
cd backend
call setup.bat
if errorlevel 1 (
    echo [ERROR] Backend setup failed!
    cd ..
    pause
    exit /b 1
)
cd ..

REM Setup Frontend
echo.
echo ========================================
echo   Setting up Frontend...
echo ========================================
cd frontend
call setup.bat
if errorlevel 1 (
    echo [ERROR] Frontend setup failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo   Complete Setup Finished!
echo ========================================
echo.
echo To start the application:
echo 1. Run: start_all.bat
echo.
echo Or manually:
echo 1. Backend: cd backend ^&^& start.bat
echo 2. Frontend: cd frontend ^&^& start.bat
echo.
pause
