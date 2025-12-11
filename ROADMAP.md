# 🎯 BetOn - Roadmap & Strategy Enhancement

## 📅 Data: 2025-12-08 10:04 UTC

---

## ✅ Concluído Hoje (2025-12-08)

### Consolidação de Equipas
- [x] Consolidação inicial de duplicados (35 → 29 → 27 equipas)
- [x] Renomeação para nomes simples (Porto, Benfica, Sporting, SC Braga)
- [x] Script de consolidação criado e testado

### Análise Pareto
- [x] Módulo backend `pareto_analyzer.py` criado
- [x] Endpoint `/api/analysis/pareto-analysis` implementado
- [x] Análise de todos os mercados (Over/Under, BTTS, 1X2)
- [x] Filtro por época implementado
- [x] Página frontend Pareto criada
- [x] Página de Mercados criada (`/analysis/markets`)

### Endpoint Filtrado
- [x] Novo endpoint `/api/analysis/pareto-teams` criado
- [x] Suporte para filtros de época e mercado
- [x] Cálculos dinâmicos de rankings
- [x] Frontend atualizado para usar novo endpoint

---

## 🔴 BLOQUEADOR CRÍTICO - Resolver PRIMEIRO

### ❌ Duplicação de Nomes de Equipas

**Problema:**
- Base de dados `beton.db` tem apenas nomes corretos (27 equipas)
- API `/pareto-teams` retorna nomes duplicados em inglês
- Dados vêm de **football-data.co.uk** (site inglês)

**Nomes Duplicados Encontrados:**
```
Database (✅ Correto):          API Response (❌ Duplicado):
- Sporting (205 jogos)         - "Sp Lisbon" (80 jogos)
- Benfica (205 jogos)          - "Sporting Clube de Portugal" (34 jogos)
- Porto (205 jogos)            - "Sport Lisboa e Benfica" (34 jogos)
- SC Braga (205 jogos)         - "FC Porto" (34 jogos)
                               - "Sp Braga" (80 jogos)
                               - "Sporting Clube de Braga" (34 jogos)
```

**Causa Raiz:**
- Collector `football_data_co_uk.py` importa dados com nomes em inglês
- Mapeamento de nomes adicionado MAS não aplicado retroativamente

**Soluções Implementadas (Parcial):**
- [x] Mapeamento `TEAM_NAME_MAP` adicionado ao collector
- [x] Método `_get_or_create_team` atualizado para normalizar nomes
- [ ] ⚠️ **FALTA:** Consolidar dados EXISTENTES na base de dados

**Próximos Passos CRÍTICOS:**

1. **Investigar Base de Dados:**
   ```bash
   # Verificar se há múltiplas bases de dados
   dir beton.db /s
   
   # Verificar qual BD o backend está a usar
   # Ver config.py ou database.py
   ```

2. **Restart Backend:**
   ```bash
   # Parar tudo
   # Executar start_all.bat
   # Testar API novamente
   ```

3. **Consolidar Duplicados Existentes:**
   ```bash
   # Executar script de consolidação
   python backend\scripts\consolidate_with_mapping.py
   ```

4. **Recarregar Dados:**
   ```bash
   # Opção 1: Reload apenas dados problemáticos
   python backend\collectors\football_data_co_uk.py
   
   # Opção 2: Reset completo (se necessário)
   python backend\reset_and_load.py
   ```

---

## 🔍 DÚVIDAS A ESCLARECER

### 1. Localização da Base de Dados
- [ ] Confirmar que só existe 1 ficheiro `beton.db`
- [ ] Verificar qual BD o backend está a usar
- [ ] Confirmar path em `config.py` ou `database.py`

### 2. Estado do Backend
- [ ] Backend está a correr?
- [ ] Precisa de restart?
- [ ] Logs mostram algum erro?

### 3. Cache do Frontend
- [ ] Fazer Ctrl+Shift+R na página Pareto
- [ ] Verificar se dados mudam
- [ ] Testar em modo incógnito

### 4. Dados Históricos
- [ ] Quando foram importados os dados?
- [ ] Há dados de múltiplas fontes?
- [ ] Precisamos de re-importar tudo?

---

## 📋 PLANO DE AÇÃO - Próxima Sessão

### Fase 1: Diagnóstico (5 min)
1. [ ] Verificar quantos ficheiros `beton.db` existem
2. [ ] Confirmar qual o backend está a usar
3. [ ] Restart do backend (`start_all.bat`)
4. [ ] Testar API: `curl http://localhost:8000/api/analysis/pareto-teams`

### Fase 2: Consolidação (10 min)
5. [ ] Se API ainda retorna duplicados → executar `consolidate_with_mapping.py`
6. [ ] Verificar resultado: `python backend\scripts\list_teams.py`
7. [ ] Testar API novamente

### Fase 3: Reload de Dados (15 min) - SE NECESSÁRIO
8. [ ] Backup da BD: `copy beton.db beton.db.backup_final`
9. [ ] Executar `reset_and_load.py` para re-importar com nomes corretos
10. [ ] Verificar que não há duplicados

### Fase 4: Verificação Final (5 min)
11. [ ] Refresh página Pareto (Ctrl+Shift+R)
12. [ ] Confirmar que só aparecem nomes portugueses
13. [ ] Testar filtros de época e mercado

---

## 🚀 Features Implementadas Hoje

### 1. ✅ Análise Pareto Completa
**Ficheiros:**
- `backend/analysis/pareto_analyzer.py`
- `backend/api/routes/analysis.py` (endpoint `/pareto-analysis`)
- `frontend/app/analysis/pareto/page.tsx`

**Funcionalidades:**
- Top 20% equipas por Win Rate
- Análise Home vs Away
- Análise de todos os mercados (Over/Under 0.5-3.5, BTTS, 1X2)
- Filtro por época
- Insights automáticos

### 2. ✅ Endpoint Filtrado
**Ficheiro:** `backend/api/routes/pareto_teams.py`

**Funcionalidades:**
- Filtro por época (todas ou específica)
- Filtro por mercado (win_rate, over_2.5, btts_yes, home_win)
- Cálculos dinâmicos de estatísticas
- Ranking automático por mercado selecionado
- Top 20% calculado dinamicamente

### 3. ✅ Página de Mercados
**Ficheiro:** `frontend/app/analysis/markets/page.tsx`

**Funcionalidades:**
- Visualização de todos os mercados
- Filtro de época (All Time vs Current Season)
- Cards visuais para cada mercado
- Insights automáticos
- Comparação histórico vs atual

---

## 🎯 Próximas Features (Após Resolver Duplicados)

### 1. Strategy Builder + Pareto
- [ ] Adicionar filtro "Top 20% apenas"
- [ ] Integrar análise Pareto nas recomendações
- [ ] Mostrar confidence score
- [ ] Destacar value bets

### 2. Value Bet Detection
- [ ] Calcular Expected Value (EV)
- [ ] Identificar odds subvalorizadas
- [ ] Alertas automáticos
- [ ] Dashboard de value bets

### 3. Multiple Bets (Acumuladores)
- [ ] Selecionar múltiplas equipas top 20%
- [ ] Calcular odds combinadas
- [ ] Mostrar lucro potencial
- [ ] Risk assessment

### 4. Dashboard Widgets
- [ ] Widget "Top 20% Hoje"
- [ ] Widget "Value Bets"
- [ ] Widget "Mercados Quentes"
- [ ] Widget "Recomendações Pareto"

---

## 📊 Estatísticas do Projeto

**Base de Dados:**
- 27 equipas (após consolidação)
- 5,176 jogos históricos
- 3 épocas de dados
- 154 equipas totais (todas as ligas)

**Endpoints Criados:**
- `/api/analysis/pareto-analysis` - Análise completa
- `/api/analysis/pareto-teams` - Rankings filtrados

**Páginas Frontend:**
- `/analysis/pareto` - Relatório Pareto
- `/analysis/markets` - Análise de Mercados

---

## 🛠️ Ficheiros Modificados Hoje

### Backend
- `backend/analysis/pareto_analyzer.py` (criado)
- `backend/api/routes/analysis.py` (atualizado)
- `backend/api/routes/pareto_teams.py` (criado)
- `backend/main.py` (registado nova rota)
- `backend/collectors/football_data_co_uk.py` (mapeamento adicionado)

### Frontend
- `frontend/app/analysis/pareto/page.tsx` (criado/reescrito 3x)
- `frontend/app/analysis/markets/page.tsx` (criado)
- `frontend/app/page.tsx` (links adicionados)
- `frontend/components/ui/badge.tsx` (criado)

### Scripts
- `backend/scripts/rename_teams.py`
- `backend/scripts/final_consolidation.py`
- `backend/scripts/consolidate_with_mapping.py`
- `backend/scripts/find_portuguese_teams.py`
- `backend/scripts/list_teams.py`
- `backend/test_pareto_markets.py`

---

## 💡 Lições Aprendidas

1. **Normalização de Dados:** Sempre normalizar nomes de equipas na importação
2. **Mapeamento de Fontes:** Sites ingleses usam nomes diferentes
3. **Consolidação Retroativa:** Mapeamento não aplica a dados existentes
4. **Testing:** Verificar API E base de dados separadamente
5. **Cache:** Frontend pode ter dados antigos em cache

---

**Última atualização:** 2025-12-08 10:04 UTC  
**Status:** 🔴 Bloqueado - Aguarda resolução de duplicados  
**Próxima Ação:** Investigar localização da BD e restart do backend
