# 🎯 BetOn - Sistema de Apostas Desportivas

Sistema automatizado de análise e estratégias de apostas desportivas com foco na Primeira Liga Portuguesa.

---

## 🚀 Início Rápido

### 1️⃣ Primeira Vez
Certifica-te que tens o **Docker Desktop** instalado e a correr.

### 2️⃣ Iniciar
```bash
# Duplo clique em:
start.bat

# Ou via terminal:
docker-compose up -d
```

### 3️⃣ Aceder
- **App:** http://localhost:3000
- **API:** http://localhost:8000/docs

---

## 📚 Documentação

- **[START_HERE.md](START_HERE.md)** - Guia rápido de uso
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Configuração Docker completa
- **[ROADMAP.md](ROADMAP.md)** - Roadmap e features

---

## 🛠️ Comandos

| Ação | Comando |
|------|---------|
| Iniciar | `start.bat` ou `docker-compose up -d` |
| Parar | `stop.bat` ou `docker-compose down` |
| Logs | `logs.bat` ou `docker-compose logs -f` |
| Reiniciar | `restart.bat` ou `docker-compose restart` |

---

## 🏗️ Estrutura

```
PRJT BetOn/
├── backend/          # FastAPI + SQLite
├── frontend/         # Next.js 14
├── docker-compose.yml
└── beton.db          # Base de dados SQLite
```

---

## ✨ Features

- ✅ Strategy Builder com Top 20% Pareto
- ✅ Análise histórica de equipas
- ✅ Acumuladores automáticos
- ✅ Preview de estratégias em tempo real
- ✅ H2H exclusion
- ✅ Sistema de odds múltiplas fontes

---

**Modo:** Paper Trading | **Custo:** €0
