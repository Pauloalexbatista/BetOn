"""
Check current database state for matches
"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.models import Match, Team
from database.session import get_db

db = next(get_db())

# Get all Primeira Liga matches
matches = db.query(Match).filter(Match.league == 'Primeira Liga').all()

print(f"📊 Database Status - Primeira Liga")
print("="*60)
print(f"Total Matches: {db.query(Match).count()}")

# Check Round data
recent = db.query(Match).order_by(Match.match_date.desc()).limit(10).all()
print("\nRecent Matches Round Data:")
for m in recent:
    print(f"[{m.match_date}] {m.home_team.name} vs {m.away_team.name} | Round: {m.round} | Season: {m.season}")
print(f"With round field: {sum(1 for m in matches if m.round)}")
print(f"With dates: {sum(1 for m in matches if m.match_date)}")
print(f"Finished: {sum(1 for m in matches if m.status == 'finished')}")
print(f"Scheduled: {sum(1 for m in matches if m.status == 'scheduled')}")

print(f"\n📅 Sample matches:")
print("-"*60)
for m in matches[:10]:
    date_str = m.match_date.strftime('%Y-%m-%d') if m.match_date else 'No date'
    score = f"{m.home_score}-{m.away_score}" if m.home_score is not None else "vs"
    print(f"{date_str} | Round: {m.round or 'None':5} | {m.home_team.name:20} {score:5} {m.away_team.name:20}")

db.close()
