# 🏛️ Império BetOn - Instruções e Chaves de API

Rei Paulo! Concluímos a limpeza completa da fortaleza:
*   ✅ Todos os ficheiros antigos no seu PC (`PRJT BetOn`) foram eliminados, preservando o repositório Git `.git`.
*   ✅ Todos os ficheiros antigos na VPS (`/root/openhands_workspace/BetOn/`) foram eliminados, mantendo o repositório Git ativo.
*   ✅ O terreno está 100% limpo e pronto para a nova criação do Alex!

---

## 🔑 1. O Nosso Arsenal de Dados (APIs & Portas)

Quando iniciarmos o novo código, use e forneça estes dados de configuração:

### 🎫 Chaves de API
*   **The Odds API Key**: `7fa6a021bc10851d916cdb9f7123304d`
    *   *Função*: Odds de futebol em tempo real e mercados de apostas.
    *   *Quota*: 500 chamadas gratuitas por dia (ativo e verificado).
*   **API-Football Key**: `a3986e5d1e1b14e9a235a71e8981eaa4`
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

> [!TIP]
> ### 🛡️ Estamos Prontos!
> Escreva a sua ideia aqui no chat. Vamos desenhar o sistema perfeito e pôr o Alex a trabalhar com total foco no novo plano!
