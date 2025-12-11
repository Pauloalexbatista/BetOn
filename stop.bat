@echo off
echo ========================================
echo   BetOn - Parando Servicos Docker
echo ========================================
echo.

docker-compose down

echo.
echo Todos os servicos foram parados.
pause
