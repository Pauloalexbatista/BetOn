@echo off
echo ========================================
echo    BetOn - Sistema de Apostas
echo ========================================
echo.
echo [1/3] Iniciando Docker containers...
docker-compose up -d --build

echo.
echo [2/3] Aguardando servicos iniciarem...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Abrindo no browser...
start http://localhost:3000
start http://localhost:8000/docs

echo.
echo ========================================
echo   PRONTO! Aplicacao a correr em:
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Pressiona qualquer tecla para ver logs...
pause >nul

docker-compose logs -f
