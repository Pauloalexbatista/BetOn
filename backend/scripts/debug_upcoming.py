
import sys
import os
# Add 'backend' to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import get_db
from analysis.strategy_preview import StrategyPreviewEngine

db = next(get_db())
engine = StrategyPreviewEngine(db)

# Strategy: Sporting + Benfica Home Win
strategy = {
    "target_outcome": "home_win",
    "leagues": ["Primeira Liga"],
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

print("--- Running Upcoming Preview ---")
try:
    result = engine.run_preview(
        conditions=strategy["conditions"],
        target_outcome=strategy["target_outcome"],
        teams=strategy["teams"],
        limit=50
    )
    
    print(f"Upcoming Matches Found: {len(result.get('upcoming_matches', {}).get('matches', []))}")
    accas = result.get('upcoming_matches', {}).get('accumulators', [])
    print(f"Upcoming Accumulators: {len(accas)}")
    
    if accas:
        print("\nFirst Accumulator:")
        print(accas[0])
    
    # Print upcoming match dates
    print("\nDates:")
    for m in result.get('upcoming_matches', {}).get('matches', [])[:5]:
        print(f"{m['date']} - {m['home']} vs {m['away']}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Raw check
from sqlalchemy import text
print("\n--- Raw DB Check ---")
with db.connection() as conn:
    res = conn.execute(text("SELECT count(*) FROM matches WHERE status='SCHEDULED' AND season='2024/2025'"))
    print(f"Total Scheduled (24/25): {res.scalar()}")
    
    res = conn.execute(text("SELECT count(*) FROM matches m JOIN teams t ON m.home_team_id = t.id WHERE m.status='SCHEDULED' AND t.name='Sporting'"))
    print(f"Sporting Scheduled (Home): {res.scalar()}")


