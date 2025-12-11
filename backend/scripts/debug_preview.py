
import sys
import os

# Add backend directory to path (parent of current script)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db
from analysis.strategy_preview import StrategyPreviewEngine

db = next(get_db())
engine = StrategyPreviewEngine(db)

# Dummy Strategy
strategy = {
    "target_outcome": "home_win",
    "min_odds": 1.05,
    "max_odds": 3.0,
    "min_probability": 0.3,
    "league_id": 1,
    "teams": ["Sporting", "Benfica"],
    "conditions": [
        {
            "entity": "Team",
            "context": "Global",
            "metric": "Golos Marcados",
            "operator": ">",
            "value": 1.5,
            "last_n_games": 5
        }
    ]
}

from sqlalchemy import text

print("Running Debug for Sporting + Benfica (2024/2025) WITH CONDITIONS...")
# Explicitly check for current season in DB first
cursor = db.execute(text("SELECT count(*) FROM matches WHERE season='2024/2025' AND status='finished'"))
print(f"DB Finished 24/25 Matches: {cursor.fetchone()[0]}")

print("--- Running Preview ---")
try:
    result = engine.run_preview(
        conditions=[], 
        target_outcome=strategy["target_outcome"], 
        teams=strategy["teams"],
        limit=50
    )
    print(f"Matches Found: {result['matches_found']}")
    print(f"Accumulators: {len(result['accumulators'])}")
    if result['accumulators']:
        print(f"Example Acca: {result['accumulators'][0]}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
