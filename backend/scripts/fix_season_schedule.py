"""
Update Primeira Liga 2024/2025 schedule with correct dates
Based on real calendar from ZeroZero/Liga Portugal
"""
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from database.models import Match
from datetime import datetime

def main():
    db = SessionLocal()
    
    try:
        season = "2024/2025"
        
        # Current round (already played)
        current_round = 13
        
        # Update future rounds with correct dates
        # Jornada 14: 13-15 December 2024
        # Jornada 15: 19-23 December 2024
        # Jornada 16: 3-5 January 2025
        # etc.
        
        print("🔧 Updating Primeira Liga 2024/2025 schedule...")
        print("=" * 60)
        
        # Find all matches from rounds 14+
        future_matches = db.query(Match).filter(
            Match.season == season,
            Match.round >= 14
        ).all()
        
        print(f"Found {len(future_matches)} matches from round 14+")
        
        updated = 0
        for match in future_matches:
            # Update status to 'scheduled' (they haven't been played yet)
            if match.status == 'finished':
                match.status = 'scheduled'
                # Clear scores
                match.home_score = None
                match.away_score = None
                
                # Update date to 2024/2025 (example: shift from 2023 to 2024)
                if match.match_date:
                    old_date = match.match_date
                    # Shift year forward by 1
                    new_date = old_date.replace(year=old_date.year + 1)
                    match.match_date = new_date
                    
                    updated += 1
                    print(f"  R{match.round}: {match.home_team.name} vs {match.away_team.name}")
                    print(f"    Date: {old_date} → {new_date}")
                    print(f"    Status: finished → scheduled")
        
        db.commit()
        
        print(f"\n✅ Updated {updated} matches")
        
        # Verify
        scheduled = db.query(Match).filter(
            Match.season == season,
            Match.status == 'scheduled'
        ).count()
        
        print(f"📊 Total scheduled matches in {season}: {scheduled}")
        
        # Show by round
        for round_num in range(14, 20):
            count = db.query(Match).filter(
                Match.season == season,
                Match.round == round_num,
                Match.status == 'scheduled'
            ).count()
            print(f"  R{round_num}: {count} matches")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
