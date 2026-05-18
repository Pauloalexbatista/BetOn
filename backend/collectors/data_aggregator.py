from collectors.api_football_client import APIFootballClient
from collectors.the_odds_client import TheOddsClient

class DataAggregator:
    def __init__(self):
        self.football_client = APIFootballClient()
        self.odds_client = TheOddsClient()
        # Mapeamento simples para normalização
        self.team_map = {
            "Sporting CP": "Sporting",
            "SL Benfica": "Benfica",
            "FC Porto": "Porto"
        }

    def normalize_team_name(self, name: str) -> str:
        return self.team_map.get(name, name)

    async def get_unified_match_data(self, league_id: int, season: int, sport_key: str):
        # Busca dados estruturais e odds
        standings = await self.football_client.get_standings(league_id, season)
        odds = await self.odds_client.get_odds(sport=sport_key)
        
        return {
            "standings": standings,
            "odds": odds,
            "metadata": {"league_id": league_id, "season": season}
        }