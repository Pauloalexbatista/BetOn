"""
The Odds API Client

This module provides a client for interacting with The Odds API (https://the-odds-api.com/).
It is the PRIMARY data source for fetching live odds for the BetOn system.

Features:
- Fetch upcoming odds for multiple sports
- Support for multiple regions (EU, US, UK, AU)
- Support for multiple markets (h2h, totals, spreads, etc.)
- Automatic quota tracking via response headers

Usage:
    from collectors.the_odds_api import TheOddsAPIClient
    
    client = TheOddsAPIClient()
    odds = await client.get_upcoming_odds("soccer_portugal_primeira_liga")
    
Configuration:
    Requires THE_ODDS_API_KEY in .env file
    Free tier: 500 requests/month

Author: BetOn Development Team
Last Updated: December 2025
"""
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
        Fetch upcoming odds for a specific sport.
        
        This is the main method for retrieving live odds data. It automatically creates
        fixtures for new matches and updates existing ones.
        
        Args:
            sport (str): Sport key from The Odds API. Common values:
                - "soccer_portugal_primeira_liga" (default)
                - "soccer_epl" (English Premier League)
                - "soccer_spain_la_liga"
                - "soccer_italy_serie_a"
                - "soccer_germany_bundesliga"
            regions (str): Comma-separated regions for bookmakers:
                - "eu" (European bookmakers, default)
                - "us" (American bookmakers)
                - "uk" (UK bookmakers)
                - "au" (Australian bookmakers)
            markets (str): Comma-separated markets to fetch:
                - "h2h" (Head-to-Head / Match Winner, default)
                - "totals" (Over/Under goals)
                - "spreads" (Handicap)
        
        Returns:
            list: List of match odds dictionaries containing:
                - id: Unique match identifier
                - sport_key: Sport identifier
                - commence_time: Match start time (ISO format)
                - home_team: Home team name
                - away_team: Away team name
                - bookmakers: List of bookmaker odds
                  
        Raises:
            httpx.HTTPError: If API request fails
            
        Examples:
            >>> client = TheOddsAPIClient()
            >>> odds = await client.get_upcoming_odds()  # Primeira Liga, h2h market
            >>> odds = await client.get_upcoming_odds(
            ...     sport="soccer_epl",
            ...     regions="uk,eu",
            ...     markets="h2h,totals"
            ... )
        
        Note:
            - Free tier limited to 500 requests/month
            - Check remaining quota in response headers (x-requests-remaining)
            - API documentation: https://the-odds-api.com/liveapi/guides/v4/
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
