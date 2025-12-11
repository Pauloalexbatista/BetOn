"""
Live Odds Collector
Fetches real odds from The Odds API for upcoming/scheduled matches.
Builds historical database by storing odds before matches start.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from database.database import SessionLocal
from database.models import Match, Team, Odds
from collectors.the_odds_api import TheOddsAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LiveOddsCollector:
    """
    Collects live odds for upcoming matches from The Odds API.
    Stores them in database to build historical odds over time.
    """
    
    # Map league names to The Odds API sport keys
    LEAGUE_MAPPING = {
        "Primeira Liga": "soccer_portugal_primeira_liga",
        "Premier League": "soccer_epl",
        "La Liga": "soccer_spain_la_liga",
        "Serie A": "soccer_italy_serie_a",
        "Bundesliga": "soccer_germany_bundesliga",
        "Ligue 1": "soccer_france_ligue_one"
    }
    
    def __init__(self):
        self.db = SessionLocal()
        self.client = TheOddsAPIClient()
        self.stats = {
            "matches_checked": 0,
            "odds_added": 0,
            "odds_updated": 0,
            "errors": 0
        }
    
    async def collect_all_leagues(self, markets: str = "h2h"):
        """
        Collect odds for all supported leagues.
        
        Args:
            markets: Comma-separated markets (h2h, totals, btts)
        """
        logger.info(f"🔍 Collecting odds for all leagues...")
        logger.info(f"   Markets: {markets}")
        
        for league_name, sport_key in self.LEAGUE_MAPPING.items():
            try:
                await self.collect_league_odds(league_name, sport_key, markets)
            except Exception as e:
                logger.error(f"❌ Error collecting {league_name}: {e}")
                self.stats["errors"] += 1
        
        self._print_summary()
    
    async def collect_league_odds(
        self, 
        league_name: str, 
        sport_key: str,
        markets: str = "h2h"
    ):
        """
        Collect odds for a specific league.
        
        Args:
            league_name: DB league name (e.g. "Primeira Liga")
            sport_key: The Odds API sport key
            markets: Markets to fetch
        """
        logger.info(f"\n📊 {league_name}")
        
        # Fetch odds from API
        odds_data = await self.client.get_upcoming_odds(
            sport=sport_key,
            markets=markets,
            regions="eu"
        )
        
        if isinstance(odds_data, dict) and "error" in odds_data:
            logger.error(f"   ❌ API Error: {odds_data['error']}")
            return
        
        if not isinstance(odds_data, list):
            logger.warning(f"   ⚠️ Unexpected response format")
            return
        
        logger.info(f"   Found {len(odds_data)} matches with odds from API")
        
        # Process each match
        for match_data in odds_data:
            try:
                await self._process_match_odds(match_data, league_name)
            except Exception as e:
                logger.error(f"   Error processing match: {e}")
                self.stats["errors"] += 1
    
    async def _process_match_odds(self, match_data: Dict, league_name: str):
        """Process odds for a single match"""
        
        home_team_name = match_data.get("home_team")
        away_team_name = match_data.get("away_team")
        commence_time = match_data.get("commence_time")
        
        # Find match in database
        match = self._find_match(home_team_name, away_team_name, commence_time, league_name)
        
        if not match:
            logger.warning(f"   ⚠️ Match not found in DB: {home_team_name} vs {away_team_name}")
            return
        
        self.stats["matches_checked"] += 1
        
        # Extract odds from bookmakers
        bookmakers = match_data.get("bookmakers", [])
        
        for bookmaker_data in bookmakers:
            bookmaker_name = bookmaker_data.get("key")
            markets_data = bookmaker_data.get("markets", [])
            
            for market in markets_data:
                market_key = market.get("key")
                outcomes = market.get("outcomes", [])
                
                # Parse outcomes into odds_data
                odds_data = self._parse_outcomes(outcomes, market_key)
                
                if odds_data:
                    # Store in database
                    self._store_odds(
                        match.id,
                        bookmaker_name,
                        market_key,
                        odds_data
                    )
    
    def _find_match(
        self, 
        home_team: str, 
        away_team: str, 
        commence_time: str,
        league_name: str
    ) -> Match:
        """Find or create match in database"""
        
        # Parse date
        try:
            match_date = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
        except:
            logger.warning(f"   Invalid date format: {commence_time}")
            return None
        
        # Find or create teams
        home = self._get_or_create_team(home_team, league_name)
        away = self._get_or_create_team(away_team, league_name)
        
        if not home or not away:
            return None
        
        # Find match within +/- 1 day window
        date_min = match_date - timedelta(days=1)
        date_max = match_date + timedelta(days=1)
        
        match = self.db.query(Match).filter(
            Match.home_team_id == home.id,
            Match.away_team_id == away.id,
            Match.match_date >= date_min,
            Match.match_date <= date_max
        ).first()
        
        # Create if doesn't exist
        if not match:
            match = Match(
                home_team_id=home.id,
                away_team_id=away.id,
                league=league_name,
                season="2024/2025",
                match_date=match_date,
                status="scheduled"
            )
            self.db.add(match)
            self.db.flush()  # Get ID
            logger.info(f"   ✅ Created fixture: {home_team} vs {away_team}")
        
        return match
    
    def _get_or_create_team(self, name: str, league: str) -> Team:
        """Get or create team by name"""
        # Try exact match first
        team = self.db.query(Team).filter(Team.name == name).first()
        
        if not team:
            # Create new team
            team = Team(name=name, league=league)
            self.db.add(team)
            self.db.flush()
            logger.info(f"   ✅ Created team: {name}")
        
        return team
    
    def _parse_outcomes(self, outcomes: List[Dict], market_key: str) -> Dict:
        """Parse outcomes into odds_data format"""
        
        odds_data = {}
        
        if market_key == "h2h":
            # h2h = 1x2 market
            for outcome in outcomes:
                name = outcome.get("name")
                price = outcome.get("price")
                
                if name and price:
                    # Map to our format
                    if name == "Draw":
                        odds_data["draw"] = price
                    else:
                        # First outcome is home, second is away
                        if "home" not in odds_data:
                            odds_data["home"] = price
                        elif "away" not in odds_data:
                            odds_data["away"] = price
        
        elif market_key == "totals":
            # Over/Under
            for outcome in outcomes:
                name = outcome.get("name")
                price = outcome.get("price")
                point = outcome.get("point")  # e.g. 2.5
                
                if name and price:
                    if name == "Over":
                        odds_data["over"] = price
                        odds_data["line"] = point
                    elif name == "Under":
                        odds_data["under"] = price
        
        elif market_key == "btts":
            # Both Teams To Score
            for outcome in outcomes:
                name = outcome.get("name")
                price = outcome.get("price")
                
                if name and price:
                    if name == "Yes":
                        odds_data["yes"] = price
                    elif name == "No":
                        odds_data["no"] = price
        
        return odds_data
    
    def _store_odds(
        self,
        match_id: int,
        bookmaker: str,
        market: str,
        odds_data: Dict
    ):
        """Store or update odds in database"""
        
        # Check if odds already exist
        existing = self.db.query(Odds).filter(
            Odds.match_id == match_id,
            Odds.bookmaker == bookmaker,
            Odds.market == market
        ).first()
        
        if existing:
            # Update existing
            existing.odds_data = odds_data
            existing.timestamp = datetime.utcnow()
            self.stats["odds_updated"] += 1
        else:
            # Create new
            new_odds = Odds(
                match_id=match_id,
                bookmaker=bookmaker,
                market=market,
                odds_data=odds_data,
                timestamp=datetime.utcnow()
            )
            self.db.add(new_odds)
            self.stats["odds_added"] += 1
        
        self.db.commit()
    
    def _print_summary(self):
        """Print collection summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 COLLECTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Matches checked: {self.stats['matches_checked']}")
        logger.info(f"Odds added: {self.stats['odds_added']}")
        logger.info(f"Odds updated: {self.stats['odds_updated']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("="*60)
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


async def main():
    """Main entry point"""
    print("="*60)
    print("LIVE ODDS COLLECTOR")
    print("Fetches real odds for upcoming matches")
    print("="*60)
    
    collector = LiveOddsCollector()
    
    # Collect h2h odds for all leagues
    # You can add more markets: "h2h,totals,btts"
    await collector.collect_all_leagues(markets="h2h")
    
    print("\n✅ Collection complete!")
    print("\nℹ️  These odds are now stored and will become historical data")
    print("   Run this script regularly to build odds history over time")


if __name__ == "__main__":
    asyncio.run(main())
