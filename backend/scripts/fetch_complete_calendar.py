"""
Complete Season Collector using APIFootball
Fetches all 34 rounds of Liga Portugal 2024/2025
"""
import sys
sys.path.insert(0, '/app')

from collectors.api_football import APIFootballClient
from database.database import SessionLocal
from database.models import Match, Team
from datetime import datetime

# Liga Portugal ID in APIFootball
LIGA_PORTUGAL_ID = 94
SEASON = 2024

def get_or_create_team(db, name: str):
    """Get or create team"""
    team = db.query(Team).filter(Team.name == name).first()
    if not team:
        team = Team(
            name=name,
            league="Primeira Liga",
            country="Portugal"
        )
        db.add(team)
        db.flush()
    return team

def main():
    db = SessionLocal()
    client = APIFootballClient()
    
    try:
        print("🔍 Fetching Liga Portugal 2024/2025 fixtures...")
        print("=" * 60)
        
        # Fetch ALL fixtures for the season
        fixtures = client.get_fixtures(
            league_id=LIGA_PORTUGAL_ID,
            season=SEASON
        )
        
        if not fixtures:
            print("❌ No fixtures found! Check API key and quota.")
            return
        
        print(f"📦 Received {len(fixtures)} fixtures from API")
        
        created = 0
        updated = 0
        errors = 0
        
        for fixture_data in fixtures:
            try:
                fixture = fixture_data['fixture']
                teams = fixture_data['teams']
                score = fixture_data.get('score', {})
                league = fixture_data['league']
                
                # Extract data
                fixture_id = fixture['id']
                match_date = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
                status = fixture['status']['short']
                
                # Map API status to our status
                if status in ['FT', 'AET', 'PEN']:
                    our_status = 'finished'
                elif status in ['NS', 'TBD', 'SUSP', 'PST']:
                    our_status = 'scheduled'
                elif status in ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE']:
                    our_status = 'live'
                else:
                    our_status = 'scheduled'
                
                # Get teams
                home_team = get_or_create_team(db, teams['home']['name'])
                away_team = get_or_create_team(db, teams['away']['name'])
                
                # Get scores
                home_score = score.get('fulltime', {}).get('home')
                away_score = score.get('fulltime', {}).get('away')
                
                # Round number
                round_num = league.get('round', '').replace('Regular Season - ', '')
                try:
                    round_num = int(round_num)
                except:
                    round_num = None
                
                # Check if match exists
                existing = db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.season == "2024/2025"
                ).first()
                
                if existing:
                    # Update
                    existing.match_date = match_date
                    existing.status = our_status
                    existing.round = round_num
                    if home_score is not None:
                        existing.home_score = home_score
                        existing.away_score = away_score
                    updated += 1
                else:
                    # Create
                    new_match = Match(
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        league="Primeira Liga",
                        season="2024/2025",
                        round=round_num,
                        match_date=match_date,
                        home_score=home_score,
                        away_score=away_score,
                        status=our_status
                    )
                    db.add(new_match)
                    created += 1
                
                if (created + updated) % 50 == 0:
                    print(f"  Progress: {created} created, {updated} updated...")
                    
            except Exception as e:
                print(f"  ❌ Error processing fixture {fixture_data.get('fixture', {}).get('id')}: {e}")
                errors += 1
                continue
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Done!")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
        print(f"   Errors: {errors}")
        
        # Verify
        total = db.query(Match).filter(Match.season == "2024/2025").count()
        finished = db.query(Match).filter(
            Match.season == "2024/2025",
            Match.status == "finished"
        ).count()
        scheduled = db.query(Match).filter(
            Match.season == "2024/2025", 
            Match.status == "scheduled"
        ).count()
        
        print(f"\n📊 Database Status:")
        print(f"   Total 2024/2025: {total}")
        print(f"   Finished: {finished}")
        print(f"   Scheduled: {scheduled}")
        
        # Show sample scheduled matches
        upcoming = db.query(Match).filter(
            Match.season == "2024/2025",
            Match.status == "scheduled"
        ).limit(5).all()
        
        if upcoming:
            print(f"\n📅 Sample Upcoming Matches:")
            for match in upcoming:
                print(f"   R{match.round}: {match.home_team.name} vs {match.away_team.name} ({match.match_date.strftime('%Y-%m-%d')})")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
