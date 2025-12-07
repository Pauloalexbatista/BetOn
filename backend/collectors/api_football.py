import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class APIFootballClient:
    """Client for API-Football (api-sports.io)"""
    
    def __init__(self):
        self.base_url = settings.api_football_base_url
        self.headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': settings.api_football_key
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers, timeout=30.0)

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Helper method for GET requests with error handling"""
        if not settings.api_football_key or settings.api_football_key == "your_api_football_key":
            logger.warning("API-Football key not configured!")
            return {"errors": ["API Key missing"]}

        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("errors"):
                logger.error(f"API-Football Error: {data['errors']}")
            
            return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error accessing API-Football: {str(e)}")
            return {"errors": [str(e)]}

    def get_status(self) -> Dict[str, Any]:
        """Check API status and quota"""
        return self._get("/status")

    def get_leagues(self, country: str = "Portugal") -> List[Dict[str, Any]]:
        """Get leagues for a specific country"""
        response = self._get("/leagues", params={"country": country})
        return response.get("response", [])

    def get_fixtures(self, league_id: int, season: int, date: str = None, next_n: int = None) -> List[Dict[str, Any]]:
        """Get fixtures for a league"""
        params = {"league": league_id, "season": season}
        if date:
            params["date"] = date
        elif next_n:
            params["next"] = next_n
            
        response = self._get("/fixtures", params=params)
        return response.get("response", [])

    def get_standings(self, league_id: int, season: int) -> List[Dict[str, Any]]:
        """Get standings for a league"""
        response = self._get("/standings", params={"league": league_id, "season": season})
        return response.get("response", [])

    def get_odds(self, fixture_id: int = None, league_id: int = None, season: int = None, page: int = 1) -> Dict[str, Any]:
        """
        Get odds.
        Can fetch by specific fixture_id OR by league+season (bulk).
        """
        params = {}
        if fixture_id:
            params["fixture"] = fixture_id
        elif league_id and season:
            params["league"] = league_id
            params["season"] = season
            params["page"] = page
            
        print(f"Fetching Odds: {params}...") # Debug
        return self._get("/odds", params=params)
