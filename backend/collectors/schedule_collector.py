
import logging
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Match, Team

# Add parent to path if needed (standard for our structure)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
from database.database import SessionLocal

logger = logging.getLogger(__name__)

class ScheduleCollector:
    """
    Collector for UPCOMING fixtures using API-Football.
    """
    
    # League IDs in API-Football
    LEAGUE_IDS = {
        "Primeira Liga": 94,
        "Premier League": 39,
        "La Liga": 140,
        "Serie A": 135,
        "Bundesliga": 78,
        "Ligue 1": 61
    }

    def __init__(self, db: Session = None):
        self.client = APIFootballClient()
        self.db = db if db else SessionLocal()

    def sync_upcoming(self, days=None):
        """Fetch scheduled matches for the rest of the season"""
        if days:
            # Original behavior: next N days
            logger.info(f"Fetching upcoming matches for next {days} days...")
            from_date = datetime.now().strftime("%Y-%m-%d")
            to_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        else:
            # New behavior: rest of season
            logger.info("Fetching ALL remaining matches for the season...")
            from_date = datetime.now().strftime("%Y-%m-%d")
            to_date = "2025-06-30"  # End of 2024/25 season
        
        count_new = 0
        
        # Current Season: 2024/2025 -> 2024 in API-Football
        season = 2024
        
        for league_name, league_id in self.LEAGUE_IDS.items():
            try:
                # Fetch fixtures
                fixtures = self.client.get_fixtures_range(league_id, season, from_date, to_date)
                
                for f in fixtures:
                    if self._process_fixture(f, league_name, season):
                        count_new += 1
                        
            except Exception as e:
                logger.error(f"Error fetching schedule for {league_name}: {e}")
                
        self.db.commit()
        logger.info(f"Schedule Sync Complete. New Scheduled Matches: {count_new}")

    def _process_fixture(self, f, league_name, season_year):
        """Process a single fixture fixture"""
        fixture = f['fixture']
        teams = f['teams']
        
        # We only want SCHEDULED matches (NS = Not Started, TBD = Time To Be Defined)
        if fixture['status']['short'] not in ['NS', 'TBD']:
            return False

        # 1. Resolve Teams
        # We need to match API-Football teams with our Football-Data.co.uk teams
        # This is the tricky part: Name matching.
        # We try to find by Name (fuzzy) or API ID if we had stored it.
        # Our current DB setup might have mixed sources. 
        # Strategy: Try exact name, then map manual overrides if needed.
        
        home_team = self._find_team(teams['home']['name'], league_name)
        away_team = self._find_team(teams['away']['name'], league_name)
        
        if not home_team or not away_team:
            # If we don't have the team from history, we prob shouldn't create it blindly 
            # OR we create it but it might duplicate if names differ slightly.
            # For now, let's skip if not found to ensure data quality
            logger.warning(f"Skipping scheduled match: {teams['home']['name']} vs {teams['away']['name']} (Teams not found)")
            return False

        match_date = datetime.fromisoformat(fixture['date'].replace("Z", "+00:00"))
        
        # 2. Check if exists
        existing = self.db.query(Match).filter(
            Match.home_team_id == home_team.id,
            Match.away_team_id == away_team.id,
            Match.match_date == match_date
        ).first()
        
        if existing:
            return False
            
        # 3. Create Match
        # Season string convention: "2025/2026"
        season_str = f"{season_year}/{season_year + 1}"
        
        new_match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=match_date,
            season=season_str,
            league=league_name,
            status="scheduled",
            # No scores or stats yet
        )
        
        # 4. Extract Round Information (Critical for Championship Structure)
        # API-Football Format: "Regular Season - 3", "Group Stage - 5", "Round of 16"
        round_str = f['league'].get('round', '')
        if round_str:
            new_match.round = self._parse_round(round_str)
            
        self.db.add(new_match)
        return True

    def _parse_round(self, round_str: str) -> str:
        """
        Extract numeric round from string if possible.
        "Regular Season - 5" -> "5"
        "Round 3" -> "3"
        Else return original string.
        """
        import re
        # Try to find the last number in the string
        match = re.search(r'(\d+)$', round_str)
        if match:
            return match.group(1)
        return round_str

    def _find_team(self, api_name, league_name):
        # 1. Exact match
        team = self.db.query(Team).filter(Team.name == api_name).first()
        if team: return team
        
        # 2. Heuristics / Common mappings (Football-Data.co.uk vs API-Football)
        # Man Utd -> Manchester United
        # Sp Lisbon -> Sporting CP
        # This list can grow. For MVP we handle a few.
        mappings = {
            "Sporting CP": "Sp Lisbon",
            "Benfica": "Benfica", # Usually match
            "FC Porto": "Porto",
            "Manchester United": "Man United",
            "Manchester City": "Man City",
            "Leicester City": "Leicester",
            "Leeds United": "Leeds",
            "Norwich City": "Norwich",
            "Nottingham Forest": "Nott'm Forest",
            "Tottenham Hotspur": "Tottenham",
            "Wolverhampton Wanderers": "Wolves",
            "Paris Saint Germain": "Paris SG",
            "Bayer Leverkusen": "Leverkusen",
            "Borussia Dortmund": "Dortmund",
            "Bayern Munich": "Bayern Munich",
            "Inter Milan": "Inter",
            "AC Milan": "Milan",
            "Atletico Madrid": "Ath Madrid",
            "Real Madrid": "Real Madrid"
            # Add more as we discover them
        }
        
        if api_name in mappings:
            target_name = mappings[api_name]
            team = self.db.query(Team).filter(Team.name == target_name).first()
            if team: return team
            
        # Reverse mapping check (if our DB has "Sporting CP" but api sends "Sp Lisbon" - unlikely given sources)
        
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = ScheduleCollector()
    collector.sync_upcoming()
