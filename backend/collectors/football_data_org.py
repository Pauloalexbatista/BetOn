"""
Football-Data.org API Client
Free tier: 12 competitions, 10 calls/minute, current season data
"""

import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FootballDataOrgClient:
    """Client for football-data.org API (FREE tier)"""
    
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        # Get API key from .env (add FOOTBALL_DATA_ORG_KEY=your_key)
        self.api_key = getattr(settings, 'football_data_org_key', None)
        self.headers = {
            'X-Auth-Token': self.api_key
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers, timeout=30.0)
    
    # Competition IDs (Free tier)
    COMPETITIONS = {
        "Premier League": "PL",      # England
        "La Liga": "PD",              # Spain (Primera Division)
        "Bundesliga": "BL1",          # Germany
        "Serie A": "SA",              # Italy
        "Ligue 1": "FL1",             # France
        "Eredivisie": "DED",          # Netherlands
        "Primeira Liga": "PPL",       # Portugal
        "Championship": "ELC",        # England 2nd tier
        "Champions League": "CL",
        "Europa League": "EL",
        "European Championship": "EC",
        "World Cup": "WC"
    }
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Helper method for GET requests"""
        if not self.api_key:
            logger.warning("Football-Data.org API key not configured!")
            return {"error": "API Key missing"}
        
        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error accessing football-data.org: {str(e)}")
            return {"error": str(e)}
    
    def get_competitions(self) -> List[Dict[str, Any]]:
        """Get all available competitions"""
        response = self._get("/competitions")
        return response.get("competitions", [])
    
    def get_matches(self, competition_code: str, status: str = "SCHEDULED") -> List[Dict[str, Any]]:
        """
        Get matches for a competition
        status: SCHEDULED, LIVE, IN_PLAY, PAUSED, FINISHED, POSTPONED, SUSPENDED, CANCELLED
        """
        response = self._get(f"/competitions/{competition_code}/matches", params={"status": status})
        return response.get("matches", [])
    
    def get_standings(self, competition_code: str) -> Dict[str, Any]:
        """Get standings/table for a competition"""
        return self._get(f"/competitions/{competition_code}/standings")
    
    def get_teams(self, competition_code: str) -> List[Dict[str, Any]]:
        """Get teams in a competition"""
        response = self._get(f"/competitions/{competition_code}/teams")
        return response.get("teams", [])
    
    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """Get detailed info for a specific match"""
        return self._get(f"/matches/{match_id}")


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    client = FootballDataOrgClient()
    
    # Get Primeira Liga scheduled matches
    print("Fetching Primeira Liga scheduled matches...")
    matches = client.get_matches("PPL", status="SCHEDULED")
    print(f"Found {len(matches)} scheduled matches")
    
    if matches:
        print("\nSample match:")
        m = matches[0]
        print(f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}")
        print(f"Date: {m['utcDate']}")
        print(f"Status: {m['status']}")
