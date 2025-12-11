"""
Fix Scheduled Matches Dates to be in Future
Shift all scheduled matches to start from tomorrow
"""
import sys
sys.path.insert(0, '/app')
from database.database import SessionLocal
from database.models import Match
from datetime import datetime, timedelta
import random

def fix_dates():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        print(f"🕒 UTC Now: {now}")
        
        # Get all scheduled matches
        matches = db.query(Match).filter(Match.status == 'scheduled').order_by(Match.round).all()
        print(f"📦 Found {len(matches)} scheduled matches to update")
        
        # Group by round to keep some structure
        by_round = {}
        for m in matches:
            r = m.round or 0
            if r not in by_round:
                by_round[r] = []
            by_round[r].append(m)
            
        # Start dates from tomorrow
        start_date = now + timedelta(days=1)
        updated_count = 0
        
        sorted_rounds = sorted(by_round.keys())
        
        current_date_base = start_date
        
        for r in sorted_rounds:
            round_matches = by_round[r]
            print(f"   Processing Round {r} ({len(round_matches)} matches) -> ~{current_date_base.date()}")
            
            for m in round_matches:
                # Add some randomness to time (15:00 - 21:00)
                hour = random.randint(15, 21)
                minute = random.choice([0, 15, 30, 45])
                
                # Spread matches over Sat/Sun if possible? 
                # For simplicity, just set them all to the base date + random time
                new_date = current_date_base.replace(hour=hour, minute=minute, second=0, microsecond=0)
                m.match_date = new_date
                updated_count += 1
            
            # Next round 1 week later
            current_date_base += timedelta(weeks=1)
            
        db.commit()
        print(f"✅ Updated {updated_count} matches to future dates")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_dates()
