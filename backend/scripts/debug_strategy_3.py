import sys
sys.path.insert(0, '/app')
from database.database import SessionLocal
from database.models import Strategy, Match, Team
from analysis.strategy_preview import StrategyPreviewEngine
from datetime import datetime
from sqlalchemy import or_

def debug_strategy():
    db = SessionLocal()
    try:
        # 1. Get Strategy
        strat = db.query(Strategy).filter(Strategy.id == 3).first()
        if not strat:
            print("❌ Strategy 3 not found")
            return
            
        print(f"📊 Analyzing Strategy 3: '{strat.name}'")
        print(f"   Type: {strat.strategy_type}")
        print(f"   Outcome: {strat.target_outcome}")
        print(f"   Leagues: {strat.leagues}")
        print(f"   Teams: {strat.teams}")
        
        # 2. Check "Scheduled" matches in DB
        now = datetime.utcnow()
        print(f"\n🕒 UTC Now: {now}")
        
        all_scheduled = db.query(Match).filter(
            Match.status == 'scheduled',
            Match.match_date > now
        ).count()
        print(f"✅ Total Future Scheduled matches in DB: {all_scheduled}")
        
        # 3. Simulate Query Construction
        query = db.query(Match).filter(
            Match.status == 'scheduled',
            Match.match_date > now
        )
        
        # Filter by Teams
        if strat.teams:
            team_ids = db.query(Team.id).filter(Team.name.in_(strat.teams)).all()
            team_ids = [t[0] for t in team_ids]
            print(f"   Target Team IDs: {team_ids}")
            
            if team_ids:
                query = query.filter(
                    or_(
                        Match.home_team_id.in_(team_ids),
                        Match.away_team_id.in_(team_ids)
                    )
                )
            else:
                print("   ⚠️ Strategy has teams names but no IDs found! Logic might fail here.")
        
        # Execute
        matches = query.order_by(Match.match_date.asc()).all()
        print(f"\n🔍 Query returned {len(matches)} matches")
        
        for m in matches:
            print(f"   - {m.match_date} | {m.home_team.name} vs {m.away_team.name} | R{m.round}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_strategy()
