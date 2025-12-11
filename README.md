# 🎯 BetOn - Smart Betting System

**Version:** 0.3.0 | **Status:** Active Development | **Cost:** €0/month

Automated sports betting analysis system with real-time odds, data quality monitoring, and intelligent strategy builder.

---

## 🚀 Quick Start

### Requirements
- **Docker Desktop** (v20+)
- **Git** (for cloning)

### First Time Setup
```bash
# Clone repository
git clone <your-repo-url>
cd "PRJT BetOn"

# Start containers
docker-compose up -d --build

# Wait ~30 seconds for startup
```

### Access
- **Dashboard:** http://localhost:3000
- **Data Quality:** http://localhost:3000/data-quality
- **API Docs:** http://localhost:8000/docs

---

## 📊 Current System State

### Data (as of Dec 11, 2025)
- **Teams:** 154 (clean, verified)
- **Matches:** 2,423 (240 scheduled)
- **Odds:** 21,606 total
  - 8,231 neutral (historical baseline)
  - 13,375 real (31 bookmakers)
- **Coverage:** ~55% and growing daily

### APIs
- **The Odds API:** ✅ Free tier (480/500 req remaining)
- **API-Football:** ⚠️ Historical only
- **Status:** Fully operational

---

## ✨ Key Features

### Data Collection
- ✅ **Live Odds Collector** - Real odds from 31 bookmakers
- ✅ **Auto-Fixture Creation** - Automatically detects new matches
- ✅ **6 European Leagues** - Primeira Liga, EPL, La Liga, Serie A, Bundesliga, Ligue 1

### Analysis & Monitoring
- ✅ **Data Quality Dashboard** - Real-time health metrics
- ✅ **Smart Team Consolidation** - Fuzzy matching with blacklist protection
- ✅ **Signal Generation** - Daily betting opportunities
- ✅ **Strategy Builder** - Top 20% Pareto analysis

### Automation
- ✅ **Background Tasks** - Non-blocking data collection
- ✅ **Manual Triggers** - Dashboard buttons for collection
- ⏳ **Cron Jobs** - Coming soon (auto-daily collection)

---

## 🎮 Daily Usage

### 1. Check Data Quality
```
Navigate to: http://localhost:3000/data-quality

Look for:
- 🟢 Green: Good (< 24h since last odds update)
- 🟡 Yellow: Warning (1-3 days)
- 🔴 Red: Critical (> 3 days)
```

### 2. Update Odds (if needed)
```
Click: "Executar Odds Collector"
Wait: ~30 seconds
Result: Fresh odds from The Odds API
```

### 3. Consolidate Duplicates (if shown)
```
If button appears: "Consolidar X Duplicados"
Click → Confirm → Done
```

### 4. Check Opportunities
```
Homepage → "Oportunidades do Dia"
Click "Analisar →" to view match details
```

---

## 🛠️ Commands

### Docker Controls
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart (after code changes)
docker-compose restart backend

# Rebuild (after dependency changes)
docker-compose up -d --build

# View logs
docker-compose logs -f backend
```

### Manual Scripts
```bash
# Collect odds (alternative to dashboard button)
cd backend
python collectors/live_odds_collector.py

# Consolidate teams
python scripts/consolidate_teams_smart.py

# Check scheduled matches
python scripts/check_scheduled.py
```

---

## 📁 Project Structure

```
PRJT BetOn/
├── backend/
│   ├── api/                  # FastAPI routes
│   │   └── routes/
│   │       ├── system.py     # Dashboard endpoints
│   │       ├── signals.py    # Betting signals
│   │       └── ...
│   ├── collectors/
│   │   ├── live_odds_collector.py  # Main data pipeline ⭐
│   │   └── the_odds_api.py         # API client
│   ├── scripts/
│   │   ├── consolidate_teams_smart.py  # Team cleanup ⭐
│   │   └── normalize_historical_odds.py
│   ├── analysis/
│   │   ├── data_quality_analyzer.py  # Dashboard data ⭐
│   │   └── scanner.py                # Signal generator
│   └── database/
│       └── models.py         # SQLAlchemy models
│
├── frontend/
│   └── app/
│       ├── data-quality/     # Quality dashboard ⭐
│       ├── page.tsx          # Homepage
│       └── ...
│
├── beton.db                  # SQLite database
├── docker-compose.yml
├── ROADMAP.md               # Product roadmap
└── README.md                # This file
```

⭐ = Critical files

---

## 🔑 Environment Variables

Required for backend:
```env
THE_ODDS_API_KEY=your_key_here
DATABASE_URL=sqlite:///./beton.db
```

Optional:
```env
API_FOOTBALL_KEY=your_key  # Not used for current season
```

---

## 📚 Documentation

- **[ROADMAP.md](ROADMAP.md)** - Product evolution and future plans
- **[Walkthrough](brain/walkthrough.md)** - Implementation details
- **[Task Tracking](brain/task.md)** - Development progress
- **[API Docs](http://localhost:8000/docs)** - Interactive Swagger UI

---

## 🎯 Button Reference

### Data Quality Dashboard Buttons

| Button | Action | Backend | Notes |
|--------|--------|---------|-------|
| **Executar Odds Collector** | Fetch live odds | `POST /api/system/collect-odds` | ~30s, creates fixtures |
| **Consolidar X Duplicados** | Merge similar teams | `POST /api/system/consolidate-teams` | Smartblacklist protected |

### Homepage Buttons

| Button | Action | Notes |
|--------|--------|-------|
| **Update Games** | ~~Update fixtures~~ | **DISABLED** - Use dashboard instead |
| **Limpar Todas** | Clear opportunities | UI only, regenerates on next scan |
| **Analisar →** | View match details | Links to `/matches?search=...` |

---

## 🚨 Important Notes

### What to Use
✅ **Data Quality Dashboard** - Primary control panel  
✅ **The Odds API** - Current data source  
✅ **live_odds_collector.py** - Main data pipeline  

### What NOT to Use
❌ **"Update Games" button** - Uses old deprecated collectors  
❌ **schedule_collector.py** - API-Football free tier doesn't support current season  
❌ **FootballDataCoUk collector** - Replaced by The Odds API  

### Key Decisions
- **Why neutral odds?** - Honesty about data quality (old odds are unreliable)
- **Why The Odds API?** - Only free API with current season data
- **Why blacklist teams?** - Manchester United ≠ Manchester City (fuzzy matching limitation)

---

## 🐛 Troubleshooting

### "Only 0% matches have odds"
**Fix:** Restart backend or wait for 5min cache expiry
```bash
docker-compose restart backend
```

### "Manchester United / City duplicates"
**Status:** ✅ Fixed in v0.3.0 (blacklist implemented)

### API Quota Exceeded
**Check:** Data Quality Dashboard (shows remaining requests)  
**Fix:** Wait until next month OR reduce collection frequency

### Docker containers won't start
```bash
# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

---

## 📈 Roadmap

### ✅ Phase 1: Foundation (Complete)
- Database, API integration, basic strategies

### ✅ Phase 2: Data Quality (Dec 2025)
- Quality dashboard, live odds, smart consolidation

### 🔄 Phase 3: Historical Building (Dec 2025 - Jan 2026)
- Daily automated collection
- 1-3 months of odds history

### ⏳ Phase 4: Advanced Analytics (Q1 2026)
- Backtesting with real odds
- Multi-market support (totals, BTTS)
- Value bet detection

### ⏳ Phase 5: Automation (Q2 2026)
- Cron-based collectors
- Auto-betting integration
- Telegram notifications

See [ROADMAP.md](ROADMAP.md) for details.

---

## 🤝 Contributing

### Development Workflow
1. Make changes in `backend/` or `frontend/`
2. Restart: `docker-compose restart backend`
3. Test via http://localhost:3000
4. Update documentation
5. Commit & push

### Key Files to Know
- `backend/collectors/live_odds_collector.py` - Main data pipeline
- `backend/api/routes/system.py` - Dashboard backend
- `frontend/app/data-quality/page.tsx` - Dashboard UI
- `backend/scripts/consolidate_teams_smart.py` - Team cleanup

---

## 📞 Support

- **Issues:** GitHub Issues (if public repo)
- **Docs:** See `brain/` folder for detailed walkthroughs
- **Logs:** `docker-compose logs -f backend`

---

## 📄 License

Private project - All rights reserved

---

**Last Updated:** December 11, 2025  
**Mode:** Paper Trading  
**Cost:** €0/month  
**Status:** Building historical database 📊
