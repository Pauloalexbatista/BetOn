import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class TheOddsClient:
    def __init__(self):
        self.api_key = os.getenv("THE_ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"

    async def get_odds(self, sport: str, markets: str = "h2h"):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/sports/{sport}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": "eu",
                    "markets": markets,
                    "oddsFormat": "decimal"
                }
            )
            return response.json()