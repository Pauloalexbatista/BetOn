"""
Simple fix: Update all matches without scores to 'scheduled'
"""
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from database.models import Match

def main():
    db = SessionLocal()
    
    try:
        # Find all matches with no score but status = 'finished'
        wrong_status = db.query(Match).filter(
            Match.status == 'finished',
            Match.home_score == None
        ).all()
        
        print(f"Found {len(wrong_status)} matches with status='finished' but no scores")
        
        # Update them
        updated = 0
        for match in wrong_status:
            print(f"  {match.home_team.name} vs {match.away_team.name} (R{match.round}, {match.match_date})")
            match.status = 'scheduled'
            updated += 1
        
        db.commit()
        
        print(f"\n✅ Updated {updated} matches to 'scheduled'")
        
        # Verify
        scheduled_count = db.query(Match).filter(Match.status == 'scheduled').count()
        print(f"Total scheduled matches now: {scheduled_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
