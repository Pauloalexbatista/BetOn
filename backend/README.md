# BetOn Backend

API backend para o sistema BetOn de automação de apostas.

## Setup

1. **Criar ambiente virtual**
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Instalar dependências**
```bash
pip install -r requirements.txt
```

3. **Configurar environment**
```bash
# Copiar .env.example para .env
copy ..\.env.example .env

# Editar .env com as tuas credenciais
```

4. **Inicializar base de dados**
```bash
python scripts\init_db.py
```

5. **Executar servidor**
```bash
uvicorn main:app --reload
```

API disponível em: `http://localhost:8000`
Documentação: `http://localhost:8000/docs`

## Estrutura

```
backend/
├── api/                # API endpoints
│   └── routes/        # Route modules
├── collectors/        # Data collectors
├── analyzers/         # Analysis engines
├── strategies/        # Betting strategies
├── bankroll/          # Bankroll management
├── automation/        # Betfair automation
├── database/          # Database models
└── scripts/           # Utility scripts
```

## API Endpoints

### Matches
- `GET /api/v1/matches/upcoming` - Próximos jogos
- `GET /api/v1/matches/{id}` - Detalhes do jogo

### Bets
- `POST /api/v1/bets/` - Criar aposta
- `GET /api/v1/bets/` - Listar apostas
- `GET /api/v1/bets/stats/summary` - Estatísticas

### Strategies
- `POST /api/v1/strategies/` - Criar estratégia
- `GET /api/v1/strategies/` - Listar estratégias
- `PATCH /api/v1/strategies/{id}/toggle` - Ativar/desativar

### Bankroll
- `GET /api/v1/bankroll/current` - Estado atual
- `GET /api/v1/bankroll/history` - Histórico

### Analysis
- `GET /api/v1/analysis/value-bets` - Value bets
- `GET /api/v1/analysis/team-stats/{id}` - Estatísticas de equipa
