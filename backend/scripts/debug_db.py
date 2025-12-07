import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match, Odds

db = SessionLocal()

print("🔍 Checking Database Content:")

# 1. Check Team Names
print("\n1. Searching for Big 3 Teams:")
teams = db.query(Team).filter(Team.name.contains("Benfica") | Team.name.contains("Porto") | Team.name.contains("Sporting")).all()
for t in teams:
    print(f"   found: '{t.name}' (ID: {t.id})")

# 2. Check Odds Count
print("\n2. Checking Odds Data:")
odds_count = db.query(Odds).count()
print(f"   Total Odds Records: {odds_count}")

# 3. Check specific match odds
if teams:
    team_id = teams[0].id
    print(f"\n3. Checking Matches for {teams[0].name}:")
    matches = db.query(Match).filter(Match.home_team_id == team_id).limit(5).all()
    for m in matches:
        print(f"   {m.match_date} - Odds: {len(m.odds)}")
        if m.odds:
            print(f"      Data: {m.odds[0].odds_data}")

db.close()
