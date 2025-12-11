@echo off
echo ========================================
echo   BetOn - Reiniciando Servicos Docker
echo ========================================
echo.

echo [1/2] A parar servicos...
docker-compose down

echo.
echo [2/2] A iniciar servicos novamente...
docker-compose up -d

echo.
echo Servicos reiniciados com sucesso!
echo.
echo Para ver os logs, execute: logs.bat
pause
