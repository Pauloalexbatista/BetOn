# 🎯 BetOn - Roadmap & Product Evolution

**Last Updated:** December 11, 2025  
**Version:** v0.3.0

---

## 🏆 Major Milestones Achieved

### Phase 1: Foundation (Complete)
- ✅ Database schema & models
- ✅ API-Football integration
- ✅ Basic strategy engine
- ✅ Manual bet placement

### Phase 2: Data Quality & Automation (December 2025) ✅
- ✅ **Data Strategy Overhaul:**
  - Normalized unreliable historical odds (8,231 → neutral 1.30)
  - Implemented live odds collection (The Odds API)
  - Built real odds database (31 bookmakers)
  
- ✅ **Data Quality Dashboard:**
  - Real-time metrics & health indicators
  - Manual trigger buttons (Odds Collector, Team Consolidation)
  - Actionable recommendations
  
- ✅ **Smart Team Management:**
  - Fuzzy duplicate detection
  - Blacklist protection (Man Utd ≠ Man City)
  - Auto-consolidation script
  
- ✅ **UX Improvements:**
  - Homepage reorganization
  - Signal deduplication
  - Functional analyze buttons

---

## 📊 Current System State (Dec 11, 2025)

### Data
- **Teams:** 154 (clean, <5 duplicates)
- **Matches:** 2,423 (240 scheduled)
- **Odds:** 21,606 total
  - 8,231 neutral (historical)
  - 13,375 real (31 bookmakers)
- **Coverage:** ~55% and growing

### APIs
- **The Odds API:** Primary source (free tier: 480/500 remaining)
- **API-Football:** Historical only (free tier limited)
- **FootballDataCoUk:** Deprecated

### Features
- Strategy builder (single + accumulators)
- Bet placement modal with Kelly calculator
- Bankroll management
- Data quality monitoring
- Signal generation

---

## 🚀 Roadmap

### Phase 3: Historical Database Building (Dec 2025 - Jan 2026)

**Goal:** Build 1-3 months of reliable odds history

**Actions:**
- [ ] Daily odds collection (automated or manual)
- [ ] Monitor API quota usage
- [ ] Track odds movement patterns
- [ ] Validate data quality weekly

**Success Metrics:**
- 30+ days of continuous odds data
- <5% missing odds for upcoming matches
- Zero API quota violations

---

### Phase 4: Advanced Analytics (Jan - Feb 2026)

**Priority: HIGH**

- [ ] **Backtesting with Real Odds:**
  - Test strategies against collected historical data
  - Compare with neutral odds baseline
  - Identify profitable patterns

- [ ] **Odds Movement Analysis:**
  - Track odds changes over time
  - Identify value opportunities
  - Alert on significant movements

- [ ] **Multiple Market Support:**
  - Add totals (Over/Under)
  - Add BTTS (Both Teams To Score)
  - Expand beyond H2H

**Priority: MEDIUM**

- [ ] **Enhanced Signals:**
  - Multi-bookmaker comparison
  - Value bet detection (best odds vs market)
  - Confidence scoring

- [ ] **Performance Dashboard:**
  - Strategy ROI visualization
  - Bookmaker comparison charts
  - Historical performance trends

---

### Phase 5: Automation & Production (Mar - Apr 2026)

**Priority: HIGH**

- [ ] **Automated Data Collection:**
  - Cron job for daily odds fetch
  - Error handling & retry logic
  - API quota monitoring alerts

- [ ] **Signal Automation:**
  - Auto-generate daily betting signals
  - Filter by user preferences
  - Telegram/Discord notifications

**Priority: MEDIUM**

- [ ] **Betting Integration:**
  - Connect to real betting platform APIs
  - Or robust web scraping
  - Auto-bet placement (with safeguards)

- [ ] **Monitoring & Alerts:**
  - Data quality degradation alerts
  - API quota warnings
  - Unusual pattern detection

---

### Phase 6: Intelligence & Optimization (Q2 2026)

- [ ] **Machine Learning:**
  - Predict odds movements
  - Optimize Kelly fractions
  - Auto-tune strategy parameters

- [ ] **Strategy Evolution:**
  - Genetic algorithms for strategy optimization
  - A/B testing framework
  - Anti-strategy analysis

- [ ] **Portfolio Management:**
  - Multi-strategy allocation
  - Risk-adjusted returns
  - Hedging strategies

---

## 🎯 Immediate Next Steps (Next 7 Days)

1. **Run Odds Collector Daily**
   - Manual: Click dashboard button
   - OR automated: Set up cron

2. **Monitor Data Growth**
   - Check dashboard daily
   - Verify API quota
   - Document any issues

3. **Commit Updated Docs**
   - Git commit all documentation
   - Tag version v0.3.0
   - Push to GitHub

4. **Plan Automation**
   - Choose: Cron vs Docker scheduler
   - Test execution
   - Set up error logging

---

## 🧹 Housekeeping (Ongoing)

### Code Cleanup
- [ ] Remove deprecated collectors
  - `FootballDataCoUkCollector`
  - Old `schedule_collector.py` (API-Football)
- [ ] Archive unused scripts
- [ ] Add docstrings to new functions

### Testing
- [ ] Unit tests for consolidation logic
- [ ] Integration test for odds collector
- [ ] API mock tests

### Documentation
- [x] Update task.md
- [x] Update walkthrough.md
- [x] Update ROADMAP.md (this file)
- [ ] Update README.md
- [ ] API documentation (Swagger)

---

## 📈 Success Metrics

### Data Quality (Target: Q1 2026)
- ✅ 0% aggregated odds (replaced with neutral)
- ✅ 30+ real bookmakers
- 🔄 80%+ odds coverage (current: 55%)
- 🔄 < 3 team duplicates (current: 1)

### Operations (Target: Q1 2026)
- 🔄 100% automated data collection
- ⏳ < 5 min data quality dashboard load
- ⏳ Zero manual interventions needed

### Business (Target: Q2 2026)
- ⏳ Profitable strategy identified
- ⏳ Positive ROI over 30 days
- ⏳ Automated betting operational

---

## 🚫 Deprecated / Removed

### Components
- ~~`backend/collectors/football_data_co_uk.py`~~ → The Odds API
- ~~`backend/collectors/schedule_collector.py`~~ → Auto-fixture creation
- ~~`frontend/app/page.tsx` "Update Games" button~~ → Disabled

### Workflows
- ~~Manual team consolidation with hard-coded mappings~~ → Smart auto-detection
- ~~Running multiple collectors separately~~ → Single live_odds_collector

---

## 💡 Lessons Learned

1. **Free APIs are viable** - The Odds API provides production-quality data
2. **Own your data** - Building historical database is worth the effort
3. **Quality > Quantity** - 1 good bookmaker > 100 bad aggregated odds
4. **UI matters** - Dashboard makes system transparent and trustworthy
5. **Blacklists are necessary** - Edge cases require manual exceptions

---

## 🤝 For Future Developers

### Key Decisions
- **Why The Odds API?** API-Football free tier doesn't cover current season
- **Why normalize old odds?** Honesty > false confidence
- **Why blacklist teams?** Fuzzy matching can't distinguish Manchester clubs
- **Why disable Update Games?** Old collectors cause data corruption

### Critical Files
- `collectors/live_odds_collector.py` - **Main data pipeline**
- `scripts/consolidate_teams_smart.py` - **Team cleanup**
- `api/routes/system.py` - **Dashboard backend**
- `app/data-quality/page.tsx` - **Dashboard frontend**

### Maintenance Commands
```bash
# Daily (required)
python collectors/live_odds_collector.py

# Weekly (if needed)
python scripts/consolidate_teams_smart.py

# Never run (deprecated)
# python scripts/update_results.py  ❌
# python collectors/schedule_collector.py  ❌
```

---

**Version History:**
- v0.3.0 (Dec 11, 2025) - Data strategy overhaul + Quality dashboard
- v0.2.1 (Dec 11, 2025) - Bet placement modal + Kelly calculator
- v0.2.0 (Dec 10, 2025) - Strategy builder + Preview
- v0.1.0 (Nov 2025) - Initial foundation

