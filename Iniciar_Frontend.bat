@echo off
title 🎨 BETON - FRONTEND (NEXT.JS)
color 0b
cls
echo =======================================================================
echo              🏛️ BEM-VINDO AO IMPERIO BETON - FRONTEND 🏛️
echo =======================================================================
echo.
echo   Este ficheiro automatiza a inicializacao da interface web de luxo.
echo.

cd /d "%~dp0frontend"

:: Verificar se a pasta node_modules existe
if not exist "node_modules" (
    echo   [+] Pasta node_modules nao encontrada. A instalar dependencias via npm install...
    npm install
)

if not exist "node_modules" (
    echo   [Erro] Falha ao instalar as dependencias. Certifique-se de que o Node.js esta instalado.
    pause
    exit /b
)

echo.
echo   [1/2] A abrir a interface do utilizador em http://localhost:3002...
start http://localhost:3002
echo.
echo   [2/2] A iniciar o servidor de desenvolvimento Next.js...
echo.
npm run dev -- -p 3002
pause
