import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

class TheOddsAPIClient:
    def __init__(self):
        self.api_key = settings.the_odds_api_key
        self.base_url = settings.the_odds_api_base_url
        
        if not self.api_key:
            print("WARNING: THE_ODDS_API_KEY not set in config!")

    async def get_upcoming_odds(self, sport: str = "soccer_portugal_primeira_liga", regions: str = "eu", markets: str = "h2h"):
        """
        Fetch upcoming odds.
        Default sport is Portuguese League (soccer_portugal_primeira_liga).
        Check docs for other sport keys: https://the-odds-api.com/sports-odds-index/
        """
        if not self.api_key:
            return {"error": "API Key missing"}

        url = f"{self.base_url}/sports/{sport}/odds/"
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": markets,
            "oddsFormat": "decimal"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                # Check quota usage from headers
                requests_remaining = response.headers.get("x-requests-remaining")
                print(f"The Odds API - Usage Left: {requests_remaining}")
                
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error fetching from The Odds API: {e}")
                return {"error": str(e)}

    async def get_sports(self):
        """Get list of available sports"""
        if not self.api_key:
            return []
            
        url = f"{self.base_url}/sports"
        params = {"apiKey": self.api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            return response.json()
