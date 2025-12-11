import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Match
from datetime import datetime, timedelta

db = SessionLocal()

total_scheduled = db.query(Match).filter(Match.status == 'scheduled').count()

today = datetime.now()
next_7 = today + timedelta(days=7)
next_30 = today + timedelta(days=30)

within_7 = db.query(Match).filter(
    Match.status == 'scheduled',
    Match.match_date >= today,
    Match.match_date <= next_7
).count()

within_30 = db.query(Match).filter(
    Match.status == 'scheduled',
    Match.match_date >= today,
    Match.match_date <= next_30
).count()

print(f'Total scheduled: {total_scheduled}')
print(f'Next 7 days: {within_7}')
print(f'Next 30 days: {within_30}')

samples = db.query(Match).filter(
    Match.status == 'scheduled'
).order_by(Match.match_date).limit(10).all()

print('\nPrimeiros 10 jogos scheduled:')
for m in samples:
    date_str = m.match_date.strftime("%Y-%m-%d %H:%M") if m.match_date else "No date"
    home = m.home_team.name if m.home_team else "?"
    away = m.away_team.name if m.away_team else "?"
    print(f'  {date_str} - {home} vs {away}')

db.close()
