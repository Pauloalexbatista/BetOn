@echo off
echo ========================================
echo   BetOn - Iniciando Ambiente Docker
echo ========================================
echo.

echo [1/2] A construir imagens Docker...
docker-compose build

echo.
echo [2/2] A iniciar servicos...
docker-compose up

echo.
echo Servicos parados.
pause
