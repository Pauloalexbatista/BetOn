# 🚀 BetOn - Como Usar

## ⚡ Iniciar o Projeto

```bash
# Duplo clique neste ficheiro:
start.bat

# Ou via terminal:
docker-compose up -d
```

**O que acontece:**
- ✅ Backend inicia na porta 8000
- ✅ Frontend inicia na porta 3000
- ✅ Hot reload ativo (mudanças automáticas)

---

## 🌐 Aceder à Aplicação

Após iniciar, abre no browser:

- **Frontend (App):** http://localhost:3000
- **Backend (API Docs):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎮 Comandos Disponíveis

### Ver Logs
```bash
logs.bat
# ou: docker-compose logs -f
```

### Reiniciar (após mudanças em dependencies)
```bash
restart.bat
# ou: docker-compose restart
```

### Parar Tudo
```bash
stop.bat
# ou: docker-compose down
```

---

## 📁 Ficheiros Importantes

- `docker-compose.yml` - Configuração dos serviços
- `start.bat` - Inicia tudo
- `stop.bat` - Para tudo
- `logs.bat` - Ver logs
- `restart.bat` - Reiniciar

**Documentação completa:** [DOCKER_SETUP.md](DOCKER_SETUP.md)

---

## ✅ Está Tudo OK?

Verifica se está tudo a funcionar:

```bash
# Ver status dos containers
docker-compose ps

# Deve mostrar 2 containers UP:
# - beton-backend
# - beton-frontend
```

---

**Dúvidas?** Lê o [DOCKER_SETUP.md](DOCKER_SETUP.md) ou [docker_quick_reference.md](file:///C:/Users/paulo/.gemini/antigravity/brain/6425e048-4c0d-4fc2-a428-f7960208d261/docker_quick_reference.md)
