import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match

db = SessionLocal()
team_count = db.query(Team).count()
match_count = db.query(Match).count()
leagues = db.query(Match.league).distinct().all()
league_names = [l[0] for l in leagues]

print(f"\n📊 Database Status:")
print(f"✅ Teams: {team_count}")
print(f"✅ Matches: {match_count}")
print(f"✅ Leagues: {len(league_names)} ({', '.join(league_names)})")

matches = db.query(Match).order_by(Match.match_date.desc()).limit(5).all()

print("\n📝 Sample Matches:")
for m in matches:
    print(f"   - {m.match_date.date()}: {m.home_team.name} vs {m.away_team.name} ({m.home_score}-{m.away_score})")
    print(f"     Stats: HS={m.home_shots} AS={m.away_shots} HC={m.home_corners} AC={m.away_corners} HY={m.home_yellow} AY={m.away_yellow}")

db.close()
