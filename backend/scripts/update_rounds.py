"""
Update Match Rounds from ZeroZero
Fetches correct round numbers and updates database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.zerozero_collector import ZeroZeroCollector
from database.session import get_db
from database.models import Match
from sqlalchemy import and_


def update_liga_portuguesa_rounds():
    """Update Liga Portuguesa rounds from ZeroZero"""
    db = next(get_db())
    collector = ZeroZeroCollector(db)
    
    print("=" * 70)
    print("🔄 Updating Liga Portuguesa Rounds from ZeroZero.pt")
    print("=" * 70)
    
    # Fetch all rounds
    print("\n📥 Fetching data from ZeroZero.pt...")
    rounds_data = collector.fetch_league_rounds("liga-portuguesa")
    
    if not rounds_data:
        print("❌ No data fetched. Check internet connection or ZeroZero.pt availability.")
        return
    
    print(f"✅ Found {len(rounds_data)} rounds")
    
    # Show summary
    total_matches = sum(len(r['matches']) for r in rounds_data)
    season = rounds_data[0]['season'] if rounds_data else 'Unknown'
    print(f"📊 Season: {season}")
    print(f"⚽ Total matches: {total_matches}")
    
    # Update database
    print("\n💾 Updating database...")
    
    updated_count = 0
    created_count = 0
    
    for round_info in rounds_data:
        round_num = round_info['round']
        season = round_info['season']
        matches = round_info['matches']
        
        print(f"\n  Jornada {round_num}: {len(matches)} matches")
        
        for match_data in matches:
            # Get or create teams
            home_team = collector._get_or_create_team(match_data['home_team'])
            away_team = collector._get_or_create_team(match_data['away_team'])
            
            # Find existing match by teams and season
            existing = db.query(Match).filter(
                and_(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.league == "Primeira Liga",
                    Match.season == season
                )
            ).first()
            
            if existing:
                # Update round number
                old_round = existing.round
                existing.round = round_num
                
                # Update date if available
                if match_data['date']:
                    existing.match_date = match_data['date']
                
                # Update score if finished
                if match_data['status'] == 'finished':
                    existing.home_score = match_data['home_score']
                    existing.away_score = match_data['away_score']
                    existing.status = 'finished'
                
                if old_round != round_num:
                    print(f"    ✏️  {home_team.name} vs {away_team.name}: Round {old_round} → {round_num}")
                
                updated_count += 1
            else:
                # Create new match
                new_match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    league="Primeira Liga",
                    season=season,
                    round=round_num,
                    match_date=match_data['date'],
                    home_score=match_data['home_score'],
                    away_score=match_data['away_score'],
                    status=match_data['status']
                )
                db.add(new_match)
                print(f"    ➕ {home_team.name} vs {away_team.name}: New match (Round {round_num})")
                created_count += 1
    
    # Commit changes
    db.commit()
    
    print("\n" + "=" * 70)
    print("✅ Update Complete!")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"  • Matches updated: {updated_count}")
    print(f"  • Matches created: {created_count}")
    print(f"  • Total processed: {updated_count + created_count}")
    print("=" * 70)
    
    db.close()


def verify_rounds():
    """Verify round numbers in database"""
    db = next(get_db())
    
    print("\n🔍 Verifying rounds in database...")
    
    # Count matches per round
    from sqlalchemy import func
    
    rounds = db.query(
        Match.round,
        func.count(Match.id).label('count')
    ).filter(
        Match.league == "Primeira Liga",
        Match.season.like("2024%")
    ).group_by(Match.round).order_by(Match.round).all()
    
    print(f"\n📊 Rounds found:")
    for round_num, count in rounds:
        print(f"  Jornada {round_num}: {count} matches")
    
    db.close()


if __name__ == "__main__":
    # Update rounds
    update_liga_portuguesa_rounds()
    
    # Verify
    verify_rounds()
