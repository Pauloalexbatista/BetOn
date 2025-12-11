"""
Fix match status: change 'finished' to 'scheduled' for future matches
"""
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from database.models import Match
from datetime import datetime

def main():
    db = SessionLocal()
    
    try:
        # Find all matches with future dates but status = 'finished'
        now = datetime.utcnow()
        
        wrong_status = db.query(Match).filter(
            Match.match_date > now,
            Match.status == 'finished'
        ).all()
        
        print(f"Found {len(wrong_status)} future matches with status='finished'")
        
        # Update them
        updated = 0
        for match in wrong_status:
            match.status = 'scheduled'
            # Clear scores if they exist
            if match.home_score is not None:
                match.home_score = None
                match.away_score = None
            updated += 1
            print(f"✅ {match.home_team.name} vs {match.away_team.name} (R{match.round}) -> scheduled")
        
        db.commit()
        
        print(f"\n✅ Updated {updated} matches to 'scheduled'")
        
        # Verify
        scheduled_count = db.query(Match).filter(Match.status == 'scheduled').count()
        print(f"Total scheduled matches now: {scheduled_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
