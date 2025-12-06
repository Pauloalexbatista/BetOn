# BetOn - Sistema de Automação de Apostas Betfair

Sistema completo de análise de mercados de apostas desportivas, automação de apostas na Betfair Exchange e gestão profissional de banca.

## 🎯 Objetivo

Analisar mercados de apostas desportivas, identificar value bets, e automatizar apostas na Betfair Exchange com gestão profissional de banca, focado inicialmente em futebol português.

## 🚀 Features

- ✅ **Integração Betfair API** - Acesso a mercados e colocação automática de apostas
- ✅ **Análise Estatística** - Forma de equipas, H2H, padrões de golos
- ✅ **Value Betting** - Identificação automática de apostas com valor
- ✅ **Machine Learning** - Modelos preditivos para resultados e golos
- ✅ **Gestão de Banca** - Kelly Criterion, stop-loss, tracking de ROI
- ✅ **Dashboard Moderno** - Interface Next.js com visualizações em tempo real
- ✅ **Paper Trading** - Modo de simulação antes de apostas reais

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.12+**
- **FastAPI** - REST API
- **SQLAlchemy** - ORM
- **Pandas** - Análise de dados
- **Scikit-learn** - Machine Learning
- **betfairlightweight** - Cliente Betfair API

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts** - Data visualization

### Database
- **SQLite** - Desenvolvimento
- **PostgreSQL** - Produção (futuro)

### APIs (Gratuitas)
- **Betfair Delayed API** - Mercados e apostas (delay 1-180s)
- **API-Football** - Dados de futebol (180 calls/hora)
- **TheOddsAPI** - Comparação de odds

## 📁 Estrutura do Projeto

```
BetOn/
├── backend/                 # Python FastAPI
│   ├── api/                # REST endpoints
│   ├── collectors/         # Data collection
│   ├── analyzers/          # Analysis & ML
│   ├── strategies/         # Betting strategies
│   ├── bankroll/           # Bankroll management
│   └── automation/         # Betfair automation
├── frontend/               # Next.js
│   └── src/
│       └── app/
│           ├── dashboard/  # Main dashboard
│           ├── analysis/   # Analysis tools
│           ├── bets/       # Bet management
│           └── settings/   # Configuration
├── database/               # DB schemas & migrations
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## 🚦 Getting Started

### Método Rápido (Batch Files) ⚡

**Primeira vez:**
```bash
# Duplo clique ou executar:
setup_all.bat
```

**Uso diário:**
```bash
# Duplo clique ou executar:
start_all.bat
```

Isso abre 2 janelas:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

Ver [BATCH_FILES.md](BATCH_FILES.md) para mais detalhes.

---

### Método Manual (Passo a Passo)

#### Prerequisites

- Python 3.12+
- Node.js 18+
- Conta Betfair (gratuita)
- Betfair Delayed API Key (gratuita)

#### Installation

**1. Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_db.py
```

**2. Setup Frontend**
```bash
cd frontend
npm install
```

**3. Configure Environment (Opcional)**
```bash
# Copiar .env.example para .env
copy .env.example .env

# Editar .env com as tuas API keys
notepad .env
```

**4. Run Development**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Aceder a `http://localhost:3000`

## 📊 Roadmap

- [x] **Fase 0:** Planning & Research
- [ ] **Fase 1:** Project Setup & Betfair Integration
- [ ] **Fase 2:** Data Collection System
- [ ] **Fase 3:** Analysis Engine
- [ ] **Fase 4:** Betting Strategies
- [ ] **Fase 5:** Bankroll Management
- [ ] **Fase 6:** Frontend Dashboard
- [ ] **Fase 7:** Automation & Monitoring

## ⚠️ Avisos Importantes

> **Legalidade:** Apostas desportivas em Portugal são reguladas pelo SRIJ. Usar apenas casas licenciadas.

> **Risco:** Apostas têm risco. Começar com valores pequenos e nunca apostar mais do que pode perder.

> **Automação:** Betfair permite automação via API oficial. Outras casas podem proibir bots nos termos de serviço.

> **Expectativas:** Mesmo com ML, não há garantias. O objetivo é ter edge estatístico a longo prazo.

## 💰 Custos

### Fase Atual (Gratuita)
- ✅ Betfair Delayed API
- ✅ API-Football free tier
- ✅ TheOddsAPI free tier
- ✅ Hosting local

### Fase Futura (Opcional)
- 💰 Betfair Live API: £299 (taxa única)
- 💰 APIs premium: $15-30/mês
- 💰 Cloud hosting: $10-20/mês

## 📝 License

Uso pessoal apenas. Não distribuir comercialmente.

## 🤝 Contributing

Projeto pessoal - não aceita contribuições externas.

---

**Desenvolvido com Antigravity** 🚀
