import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class APIFootballClient:
    def __init__(self):
        self.api_key = os.getenv("API_FOOTBALL_KEY")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": self.api_key
        }

    async def get_standings(self, league_id: int, season: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/standings",
                headers=self.headers,
                params={"league": league_id, "season": season}
            )
            return response.json()