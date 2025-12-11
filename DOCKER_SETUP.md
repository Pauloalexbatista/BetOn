# 🐳 BetOn - Guia Docker Setup

## 📋 Pré-requisitos

1. **Docker Desktop para Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Instalar e reiniciar o PC
   - Verificar instalação: `docker --version`

## 🚀 Início Rápido

### Primeira Vez (Setup Inicial)

1. **Fechar todos os servidores atuais** (Python, Next.js)
   - Fecha todas as janelas de terminal
   - Para processos nas portas 3000 e 8000

2. **Executar o setup**
   ```bash
   # Duplo-clique no ficheiro:
   start.bat
   ```

   Isto vai:
   - ✅ Construir as imagens Docker
   - ✅ Iniciar Backend (porta 8000)
   - ✅ Iniciar Frontend (porta 3000)
   - ✅ Conectar tudo automaticamente

3. **Aguardar**
   - Primeira vez demora ~5-10min (download de imagens)
   - Depois é instantâneo!

4. **Aceder à aplicação**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

---

## 🎮 Comandos Diários

### Iniciar Tudo
```bash
start.bat
```
Inicia backend + frontend numa só janela

### Parar Tudo
```bash
stop.bat
```
ou pressiona `Ctrl+C` na janela

### Reiniciar (Após mudanças no código)
```bash
restart.bat
```
**IMPORTANTE**: Usa isto quando mudas código Python!

### Ver Logs
```bash
logs.bat
```
Ver logs de backend e frontend em tempo real

---

## 🔥 Hot Reload

### Frontend (Next.js)
✅ **Automático** - Mudas ficheiro `.tsx`, refresh automático

### Backend (Python)
✅ **Automático** - Mudas ficheiro `.py`, servidor reinicia sozinho
⚠️ Se não funcionar, usa: `restart.bat`

---

## 🛠️ Comandos Avançados

### Reconstruir Imagens (Após mudar dependencies)
```bash
docker-compose build --no-cache
docker-compose up
```

### Ver Estado dos Containers
```bash
docker-compose ps
```

### Entrar no Container (Debug)
```bash
# Backend
docker exec -it beton-backend /bin/bash

# Frontend  
docker exec -it beton-frontend /bin/sh
```

### Limpar Tudo (Reset completo)
```bash
docker-compose down -v
docker system prune -a
```

---

## 📁 Estrutura de Ficheiros

```
PRJT BetOn/
├── docker-compose.yml      # Orquestração de serviços
├── start.bat               # ⭐ Iniciar tudo
├── stop.bat                # ⭐ Parar tudo
├── restart.bat             # ⭐ Reiniciar
├── logs.bat                # Ver logs
│
├── backend/
│   ├── Dockerfile          # Configuração Docker backend
│   ├── .dockerignore       # Ficheiros a ignorar
│   └── ... (código Python)
│
└── frontend/
    ├── Dockerfile          # Configuração Docker frontend
    ├── .dockerignore       # Ficheiros a ignorar
    └── ... (código Next.js)
```

---

## 🐛 Troubleshooting

### Erro: "Port already in use"
```bash
# Ver o que está a usar a porta
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Matar processo (substitui PID)
taskkill /PID <numero> /F
```

### Erro: "Cannot connect to Docker daemon"
- Verifica se Docker Desktop está a correr
- Reinicia Docker Desktop

### Hot Reload não funciona
```bash
restart.bat
```

### Mudaste requirements.txt ou package.json
```bash
stop.bat
docker-compose build --no-cache
start.bat
```

### Erro de Base de Dados
- A BD `beton.db` está mapeada do host
- Se corrompida, backup e recria

---

## 🚀 Deploy para Produção

### Opção 1: Railway.app (Recomendado)
1. Cria conta em railway.app
2. Liga GitHub repo
3. Railway deteta `docker-compose.yml`
4. Deploy automático!

### Opção 2: Render.com
1. Cria conta em render.com
2. New > Web Service
3. Conecta repo
4. Deploy!

### Opção 3: VPS (Hetzner/DigitalOcean)
```bash
# No servidor
git clone <repo>
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ Vantagens deste Setup

| Antes | Depois |
|-------|--------|
| 3 janelas separadas | **1 janela única** |
| Restart manual | **Auto-reload** |
| Problemas de dependencies | **Ambiente isolado** |
| Deploy complexo | **Docker = produção** |
| Configuração manual | **1 comando** |

---

## 📞 Suporte

**Problemas?**
1. Verifica logs: `logs.bat`
2. Restart: `restart.bat`
3. Reset completo: `docker-compose down && docker-compose up --build`

**Tudo OK?**
- Frontend: http://localhost:3000 ✅
- Backend: http://localhost:8000/docs ✅
- Mudas código → Refresh automático ✅
