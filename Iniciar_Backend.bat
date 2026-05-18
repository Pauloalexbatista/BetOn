@echo off
title 🚀 BETON - BACKEND (FASTAPI)
color 0a
cls
echo =======================================================================
echo               🏛️ BEM-VINDO AO IMPERIO BETON - BACKEND 🏛️
echo =======================================================================
echo.
echo   Este ficheiro automatiza a inicializacao do motor quantitativo.
echo.

cd /d "%~dp0backend"

:: Verificar/Criar Ambiente Virtual
if not exist ".venv" (
    echo   [+] Ambiente virtual nao encontrado. A criar...
    python -m venv .venv
)

if not exist ".venv" (
    echo   [Erro] Falha ao criar o ambiente virtual .venv. Certifique-se de que o Python esta instalado e no PATH.
    pause
    exit /b
)

echo   [+] A ativar o ambiente virtual .venv...
call .venv\Scripts\activate.bat

:: Verificar se dependencias estao instaladas (por exemplo, se fastapi esta disponivel)
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo   [+] A instalar as dependencias em requirements.txt...
    pip install -r requirements.txt
)

python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo   [Erro] Falha ao instalar as dependencias. Certifique-se de que o pip esta a funcionar.
    pause
    exit /b
)

echo.
echo   [1/2] A abrir a documentacao da API em http://localhost:8001/docs...
start http://localhost:8001/docs
echo.
echo   [2/2] A iniciar o servidor local do Backend uvicorn...
echo.
uvicorn main:app --reload --port 8001
pause
