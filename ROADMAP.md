# 🎯 BetOn - Roadmap & Strategy Enhancement

## 📅 Data: 2025-12-11 02:00 UTC

---

## ✅ Concluído Nesta Sessão (2025-12-10/11)

### 🛠️ Bet Placement & Bankroll Management
- [x] **Modal de Aposta:** Integrado na diretoria de Estratégias (`frontend/components/BetPlacementModal.tsx`).
- [x] **Calculadora Kelly:** Integrada no modal de aposta para sugestão de stake ideal.
- [x] **API Schema Update:** Atualizado `bets.py` para retornar objetos `Team` completos (Fix para erro 500 e React Objects Error).
- [x] **Frontend Fixes:** Atualizado `bets/page.tsx` e `bankroll/page.tsx` para renderizar objetos de equipa.
- [x] **Run Script:** Validado `RUN.bat` para startup robusto do Docker.

### 🧠 Strategy Builder & Preview
- [x] **H2H Filtering:** Corrigido filtro para evitar jogos H2H (jogos entre duas equipas selecionadas) nas previsões.
- [x] **Strategy Preview:** Corrigida lógica de acumuladores para agrupar corretamente por Rounds.
- [x] **Odds Reais:** Preview agora usa odds reais da base de dados.
- [x] **Schema Migration:** Script `migrate_v2_targets.py` criado e executado.

### 🐛 Bug Fixes
- [x] Resolvido erro "Objects are not valid as a React child" no frontend.
- [x] Resolvido erro 500 no endpoint de criação de apostas (Pydantic validation).
- [x] Resolvido erro de props no `UniversalFilter`.

---

## 📋 Pendente / Próximos Passos

### 1. Automação & Execução (Alta Prioridade)
- [ ] **Daemon de Apostas:** Criar worker para verificar sinais e colocar apostas automaticamente.
- [ ] **Integração Real:** Conectar a APIs de casas de apostas reais (ou scraper mais robusto).
- [ ] **Notificações:** Alertas via Telegram/Discord quando uma aposta é colocada.

### 2. Strategy Analysis (Média Prioridade)
- [ ] **Backtest Robusto:** Melhorar backtester para simular seasons completas com banca dinâmica.
- [ ] **Strategy Optimization:** Algoritmo para sugerir melhorias em estratégias existentes.
- [ ] **Comparator:** Comparar performance de estratégia vs Anti-Estratégia.

### 3. Housekeeping (Baixa Prioridade)
- [ ] **Cleanup:** Remover código morto e scripts de debug antigos.
- [ ] **Tests:** Adicionar testes unitários para cálculo de Kelly e filtros de estratégia.
- [ ] **Docker:** Otimizar build time dos containers.

---

## 📊 Status Atual
- **Versão:** v0.2.1
- **Banca:** Funcional (Manual + Simulação)
- **Estratégias:** Funcional (Single + Accas Preview)
- **API:** Estável
- **Frontend:** Estável

---

**Última atualização:** 2025-12-11 02:00 UTC
