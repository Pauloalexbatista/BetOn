# BetOn - Batch Files Guide

## 📁 Batch Files Criados

### Setup (Primeira Vez)

**`setup_all.bat`** - Setup completo (backend + frontend)
```bash
# Executar na raiz do projeto
setup_all.bat
```

**`backend\setup.bat`** - Setup apenas do backend
- Cria virtual environment
- Instala dependências Python
- Inicializa base de dados

**`frontend\setup.bat`** - Setup apenas do frontend
- Instala dependências Node.js

---

### Start (Uso Diário)

**`start_all.bat`** - Inicia tudo (backend + frontend)
```bash
# Executar na raiz do projeto
start_all.bat
```
Abre 2 janelas:
- Backend em http://localhost:8000
- Frontend em http://localhost:3000

**`backend\start.bat`** - Inicia apenas backend
- Ativa virtual environment
- Verifica/cria base de dados
- Inicia FastAPI server

**`frontend\start.bat`** - Inicia apenas frontend
- Inicia Next.js dev server

---

## 🚀 Como Usar

### Primeira Vez (Setup)

1. **Abrir terminal na pasta BetOn**
   ```
   cd c:\Users\paulo\.gemini\antigravity\playground\quantum-gravity\BetOn
   ```

2. **Executar setup completo**
   ```
   setup_all.bat
   ```

3. **Aguardar instalação** (pode demorar alguns minutos)

---

### Uso Normal (Depois do Setup)

1. **Duplo clique em `start_all.bat`**
   
   OU

2. **Executar no terminal:**
   ```
   start_all.bat
   ```

3. **Aceder à aplicação:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 🛠️ Troubleshooting

### Erro: "Python not found"
- Instalar Python 3.12+
- Adicionar ao PATH

### Erro: "Node.js not found"
- Instalar Node.js 18+
- Reiniciar terminal

### Erro: "Virtual environment not found"
- Executar `backend\setup.bat` primeiro

### Erro: "Dependencies not installed"
- Executar `frontend\setup.bat` primeiro

### Backend não inicia
- Verificar se porta 8000 está livre
- Ver logs na janela do backend

### Frontend não inicia
- Verificar se porta 3000 está livre
- Verificar se backend está a correr
- Ver logs na janela do frontend

---

## 📝 Notas

- **Primeira vez:** Usar `setup_all.bat` ou `setup.bat` individual
- **Uso diário:** Usar `start_all.bat` ou `start.bat` individual
- **Parar servidores:** Ctrl+C na janela ou fechar janela
- **Logs:** Visíveis nas janelas abertas pelos batch files

---

## ⚡ Atalhos Rápidos

Podes criar atalhos no desktop para:
- `start_all.bat` - Inicia tudo com duplo clique
- `backend\start.bat` - Apenas backend
- `frontend\start.bat` - Apenas frontend
