# 🏛️ Império BetOn - Instruções e Chaves de API

Rei Paulo! Concluímos a limpeza completa da fortaleza:
*   ✅ Todos os ficheiros antigos no seu PC (`PRJT BetOn`) foram eliminados, preservando o repositório Git `.git`.
*   ✅ Todos os ficheiros antigos na VPS (`/root/openhands_workspace/BetOn/`) foram eliminados, mantendo o repositório Git ativo.
*   ✅ O terreno está 100% limpo e pronto para a nova criação do Alex!

---

## 🔑 1. O Nosso Arsenal de Dados (APIs & Portas)

Quando iniciarmos o novo código, use e forneça estes dados de configuração:

### 🎫 Chaves de API
*   **The Odds API Key**: `[REMOVIDO POR SEGURANÇA - Consultar .env do backend]`
    *   *Função*: Odds de futebol em tempo real e mercados de apostas.
    *   *Quota*: 500 chamadas gratuitas por dia.
*   **API-Football Key**: `[REMOVIDO POR SEGURANÇA - Consultar .env do backend]`
    *   *Função*: Resultados históricos, classificações, calendários e dados oficiais das ligas.
    *   *Base URL*: `https://v3.football.api-sports.io`

### 🔌 Portas de Rede Seguras na VPS
Para evitar qualquer conflito com os outros serviços ativos da VPS, utilize sempre estas portas:
*   🌐 **BetOn Frontend (Next.js)**: Porta do Host **`3002`** (mapeia para `3000` no container).
*   🚀 **BetOn Backend (FastAPI)**: Porta do Host **`8001`** (mapeia para `8000` no container).

---

## 🤝 2. O Nosso Fluxo de Trabalho de IA

1.  **A Sua Ideia**: Escreva a sua ideia e as regras do novo `BetOn` aqui no chat.
2.  **A Minha Lógica (Olímpia)**: Eu estruturo a arquitetura, crio os ficheiros de planeamento, e gero os prompts exatos de comando.
3.  **A Execução (Alex)**: Copia os meus prompts para o **OpenHands** (porta `3000`) e deixa o **Alex** escrever o código, instalar as dependências e subir os containers Docker.

---

## 🚀 3. Como Iniciar Localmente (Windows Shortcuts)

Criámos dois atalhos automáticos e inteligentes na raiz do projeto para poderes testar e desenvolver no teu PC de forma rápida e autónoma:

1.  **[Iniciar_Backend.bat](file:///c:/Users/paulo/.gemini/antigravity/playground/core-omega/PRJT%20BetOn/Iniciar_Backend.bat)**:
    *   Verifica se existe um ambiente virtual (`.venv`) e cria-o caso não exista.
    *   Instala todas as dependências (`pip install -r requirements.txt`) automaticamente.
    *   Abre automaticamente a documentação interativa da API no teu navegador (`http://localhost:8001/docs`).
    *   Inicia o servidor FastAPI na porta **`8001`**.
2.  **[Iniciar_Frontend.bat](file:///c:/Users/paulo/.gemini/antigravity/playground/core-omega/PRJT%20BetOn/Iniciar_Frontend.bat)**:
    *   Verifica se a pasta `node_modules` existe e corre `npm install` caso esteja em falta.
    *   Configura as variáveis de ambiente locais necessárias (`frontend/.env.local`).
    *   Abre automaticamente o Next.js no teu navegador (`http://localhost:3002`).
    *   Inicia o servidor de desenvolvimento Next.js na porta **`3002`**.

---

> [!TIP]
> ### 🛡️ Estamos Prontos!
> Corre os dois ficheiros `.bat` para lançares todo o ecossistema localmente e começares os teus testes e simulações com total facilidade!

