@echo off
echo ========================================
echo   BetOn Backend - Starting...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_backend.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if database exists
if not exist "beton.db" (
    echo.
    echo [WARNING] Database not found!
    echo [2/3] Initializing database...
    python scripts\init_db.py
    if errorlevel 1 (
        echo [ERROR] Database initialization failed!
        pause
        exit /b 1
    )
) else (
    echo [2/3] Database found - skipping initialization
)

REM Start FastAPI server
echo.
echo [3/3] Starting FastAPI server...
echo.
echo ========================================
echo   Backend running at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload

pause
