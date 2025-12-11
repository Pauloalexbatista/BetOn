import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Match, Team
from sqlalchemy import distinct, desc

def test_filters():
    db = SessionLocal()
    try:
        print("--- Testing Leagues ---")
        leagues = db.query(Match.league).distinct().filter(Match.league.isnot(None)).order_by(Match.league).all()
        print(f"Leagues found: {[l[0] for l in leagues]}")
        
        print("\n--- Testing Seasons ---")
        seasons = db.query(Match.season).distinct().filter(Match.season.isnot(None)).order_by(Match.season.desc()).all()
        print(f"Seasons found: {[s[0] for s in seasons]}")

        print("\n--- Testing Team Map Union ---")
        team_league_query = db.query(Match.home_team_id, Match.league).distinct().union(
                            db.query(Match.away_team_id, Match.league).distinct())
        
        results = team_league_query.all()
        print(f"Team-League Map Entries: {len(results)}")
        if len(results) > 0:
            print(f"Sample: {results[:3]}")

        print("\n--- Testing Teams ---")
        teams = db.query(Team).limit(5).all()
        print(f"Teams: {[t.name for t in teams]}")

        
    finally:
        db.close()

if __name__ == "__main__":
    test_filters()
