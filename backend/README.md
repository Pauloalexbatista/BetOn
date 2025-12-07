# BetOn Backend
API backend for the BetOn sports betting analysis platform.

## Setup
1. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
# This creates beton.db and loads initial data
python reset_and_load.py 
```

4. **Run Server**
```bash
uvicorn main:app --reload
```
API: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

## Structure
```
backend/
├── api/                # API Routes (matches, bets, analysis, system)
├── collectors/         # Data Collectors (football-data.co.uk, API-Football)
├── analysis/           # Engines (Standings, Backtester)
├── database/           # Models & DB Config
├── scripts/            # Automation (update_results.py)
└── main.py             # App Entrypoint
```

## features
- **Multi-Source Data**: Hybrid of `football-data.co.uk` (Stats) and `API-Football` (Schedule).
- **Universal Filters**: Deep filtering by League, Team, Season, Date.
- **Dynamic Standings**: "Time-travel" capable league tables.
- **Automation**: Daily background updates for results and fixtures.
