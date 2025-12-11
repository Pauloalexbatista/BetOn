"""
Quick Fixtures Update
Fetches upcoming fixtures for the next 7 days to enable odds collection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Match, Team
from collectors.api_football import APIFootballClient
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_upcoming_fixtures():
    """Fetch fixtures for next 7 days"""
    db = SessionLocal()
    client = APIFootballClient()
    
    try:
        # Calculate date range
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        from_date = today.strftime("%Y-%m-%d")
        to_date = next_week.strftime("%Y-%m-%d")
        
        logger.info(f"Fetching fixtures from {from_date} to {to_date}")
        
        # Liga IDs
        leagues = {
            "Primeira Liga": 94,
            "Premier League": 39,
            "La Liga": 140,
            "Serie A": 135,
            "Bundesliga": 78,
            "Ligue 1": 61
        }
        
        total_added = 0
        
        for league_name, league_id in leagues.items():
            logger.info(f"\n📊 {league_name}")
            
            # Fetch fixtures
            fixtures = client.get_fixtures_range(
                league_id=league_id,
                season=2024,
                from_date=from_date,
                to_date=to_date
            )
            
            if not fixtures:
                logger.warning(f"  No fixtures found")
                continue
            
            logger.info(f"  Found {len(fixtures)} fixtures from API")
            
            # Process
            for f in fixtures:
                try:
                    if process_fixture(db, f, league_name):
                        total_added += 1
                except Exception as e:
                    logger.error(f"  Error: {e}")
        
        db.commit()
        logger.info(f"\n✅ Added {total_added} new upcoming fixtures")
        
    finally:
        db.close()

def process_fixture(db, fixture_data, league_name):
    """Process a single fixture"""
    
    fixture = fixture_data.get('fixture', {})
    teams = fixture_data.get('teams', {})
    league = fixture_data.get('league', {})
    
    # Only scheduled/not started
    if fixture.get('status', {}).get('short') not in ['NS', 'TBD']:
        return False
    
    # Get team names
    home_name = teams.get('home', {}).get('name')
    away_name = teams.get('away', {}).get('name')
    
    if not home_name or not away_name:
        return False
    
    # Find or create teams
    home_team = get_or_create_team(db, home_name, league_name)
    away_team = get_or_create_team(db, away_name, league_name)
    
    # Parse date
    date_str = fixture.get('date')
    try:
        match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        logger.warning(f"  Invalid date: {date_str}")
        return False
    
    # Check if exists
    existing = db.query(Match).filter(
        Match.home_team_id == home_team.id,
        Match.away_team_id == away_team.id,
        Match.match_date == match_date
    ).first()
    
    if existing:
        return False
    
    # Create match
    new_match = Match(
        api_id=fixture.get('id'),
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        league=league_name,
        season="2024/2025",
        round=parse_round(league.get('round')),
        match_date=match_date,
        status="scheduled"
    )
    
    db.add(new_match)
    logger.info(f"  ✅ {home_name} vs {away_name} - {match_date.strftime('%Y-%m-%d %H:%M')}")
    return True

def get_or_create_team(db, name, league):
    """Get or create team"""
    team = db.query(Team).filter(Team.name == name).first()
    
    if not team:
        team = Team(name=name, league=league)
        db.add(team)
        db.flush()
    
    return team

def parse_round(round_str):
    """Extract round number"""
    if not round_str:
        return None
    
    import re
    match = re.search(r'(\d+)$', str(round_str))
    return match.group(1) if match else round_str

if __name__ == "__main__":
    print("="*60)
    print("FETCHING UPCOMING FIXTURES (Next 7 Days)")
    print("="*60)
    fetch_upcoming_fixtures()
    print("\n✅ Done!")
