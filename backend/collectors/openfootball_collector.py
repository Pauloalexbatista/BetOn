"""
OpenFootball Collector - FREE Public Domain Data
No API key required! Direct JSON access from GitHub
"""

import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime
from database.database import SessionLocal
from database.models import Match, Team

logger = logging.getLogger(__name__)

class OpenFootballCollector:
    """
    Collector for openfootball/football.json
    License: Public Domain - Use freely!
    Source: https://github.com/openfootball/football.json
    """
    
    BASE_URL = "https://raw.githubusercontent.com/openfootball/football.json/master"
    
    # Available leagues (2024-25 season)
    LEAGUES = {
        "Primeira Liga": "2024-25/pt.1.json",          # Portugal
        "Premier League": "2024-25/en.1.json",         # England
        "La Liga": "2024-25/es.1.json",                # Spain
        "Bundesliga": "2024-25/de.1.json",             # Germany
        "Serie A": "2024-25/it.1.json",                # Italy
        "Ligue 1": "2024-25/fr.1.json",                # France
        "Champions League": "2024-25/cl.json",         # UEFA CL
    }
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        self.db = SessionLocal()
    
    def fetch_league_data(self, league_name: str) -> Dict[str, Any]:
        """Fetch JSON data for a league"""
        if league_name not in self.LEAGUES:
            logger.error(f"League {league_name} not available")
            return {}
        
        url = f"{self.BASE_URL}/{self.LEAGUES[league_name]}"
        logger.info(f"Fetching {league_name} from {url}")
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching {league_name}: {e}")
            return {}
    
    def sync_league(self, league_name: str):
        """Sync all matches for a league"""
        data = self.fetch_league_data(league_name)
        
        if not data:
            logger.warning(f"No data for {league_name}")
            return
        
        league_info = data.get("name", league_name)
        matches = data.get("matches", [])
        
        logger.info(f"Processing {league_info}: {len(matches)} matches")
        
        matches_added = 0
        
        for match in matches:
            if self._process_match(match, league_name):
                matches_added += 1
        
        self.db.commit()
        logger.info(f"✅ {league_name}: {matches_added} new matches added")
    
    def _process_match(self, match: Dict, league_name: str) -> bool:
        """Process a single match"""
        try:
            # Extract round from match data
            round_name = match.get("round", "Unknown")
            
            # Extract teams
            team1_name = match.get("team1", "")
            team2_name = match.get("team2", "")
            
            # Find or create teams
            home_team = self._get_or_create_team(team1_name, league_name)
            away_team = self._get_or_create_team(team2_name, league_name)
            
            if not home_team or not away_team:
                return False
            
            # Extract date
            date_str = match.get("date")
            time_str = match.get("time", "00:00")
            if not date_str:
                logger.warning(f"No date for {team1_name} vs {team2_name}")
                return False
            
            # Combine date and time
            datetime_str = f"{date_str}T{time_str}:00"
            match_date = datetime.fromisoformat(datetime_str)
            
            # Check if match exists
            existing = self.db.query(Match).filter(
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
                Match.match_date == match_date
            ).first()
            
            if existing:
                # Update scores if available
                score = match.get("score", {})
                if score:
                    ft = score.get("ft", [])
                    if len(ft) == 2:
                        existing.home_score = ft[0]
                        existing.away_score = ft[1]
                        existing.status = "finished"
                return False
            
            # Create new match
            new_match = Match(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date,
                season="2024/2025",
                league=league_name,
                round=self._extract_round_number(round_name),
                status="scheduled"
            )
            
            # Add scores if available
            score = match.get("score", {})
            if score:
                ft = score.get("ft", [])
                if len(ft) == 2:
                    new_match.home_score = ft[0]
                    new_match.away_score = ft[1]
                    new_match.status = "finished"
            
            self.db.add(new_match)
            return True
            
        except Exception as e:
            logger.error(f"Error processing match: {e}")
            return False
    
    def _get_or_create_team(self, team_name: str, league: str):
        """Find or create team"""
        if not team_name:
            return None
        
        # Try exact match
        team = self.db.query(Team).filter(Team.name == team_name).first()
        if team:
            return team
        
        # Create new team
        new_team = Team(name=team_name, league=league)
        self.db.add(new_team)
        self.db.flush()  # Get ID
        return new_team
    
    def _extract_round_number(self, round_name: str) -> str:
        """Extract round number from name"""
        import re
        match = re.search(r'(\d+)', round_name)
        if match:
            return match.group(1)
        return round_name
    
    def sync_all_leagues(self):
        """Sync all available leagues"""
        for league_name in self.LEAGUES.keys():
            logger.info(f"\n{'='*60}")
            logger.info(f"Syncing {league_name}")
            logger.info(f"{'='*60}")
            self.sync_league(league_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    collector = OpenFootballCollector()
    
    print("=" * 60)
    print("OpenFootball Data Collector")
    print("FREE - Public Domain - No API Key Required!")
    print("=" * 60)
    print()
    
    # Sync Primeira Liga
    collector.sync_league("Primeira Liga")
    
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)
