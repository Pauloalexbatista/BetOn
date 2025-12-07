# BetOn - Quick Start Guide

## 🚀 Início Rápido (5 minutos)

### 1. Backend Setup
```bash
cd c:\Users\paulo\.gemini\antigravity\playground\quantum-gravity\BetOn\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_db.py
uvicorn main:app --reload
```

✅ Backend: http://localhost:8000
✅ API Docs: http://localhost:8000/docs

### 2. Frontend Setup (nova janela)
```bash
cd c:\Users\paulo\.gemini\antigravity\playground\quantum-gravity\BetOn\frontend
npm install
npm run dev
```

✅ Frontend: http://localhost:3000

---

## 🎯 Próximos Passos

1. ✅ Testar API endpoints em `/docs`
2. ✅ Ver landing page em `http://localhost:3000`
3. [ ] Configurar API keys
4. [ ] Implementar data collectors
5. [ ] Desenvolver dashboard

---

## ⚠️ Importante

- Sistema em modo **Paper Trading** (simulação)
- Não coloca apostas reais até configurares
- Testar tudo antes de ativar Live API (£299)

---

Para mais detalhes, ver [walkthrough.md](file:///C:/Users/paulo/.gemini/antigravity/brain/59799724-a96d-402a-8486-a53195147b6c/walkthrough.md)
