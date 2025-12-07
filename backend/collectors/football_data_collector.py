import logging
import time
import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from database.database import SessionLocal
from database.models import Team, Match, Odds
from collectors.api_football import APIFootballClient
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class FootballDataCollector:
    """
    Collector for API-Football data.
    Designed to be efficient with API quota (100 req/day).
    Strategy: Fetch heavy data (entire seasons) in single calls.
    """

    def __init__(self, db: Session = None):
        self.client = APIFootballClient()
        self.db = db if db else SessionLocal()
        
    def check_quota(self) -> bool:
        """Check if we have enough requests left"""
        status = self.client.get_status()
        if not status or "response" not in status:
            logger.error("Could not check API quota")
            return False
            
        requests = status.get("response", {}).get("requests", {})
        current = requests.get("current", 0)
        limit = requests.get("limit_day", 100)
        
        logger.info(f"API Quota: {current}/{limit}")
        
        if current >= limit - 5: # Safety buffer
            logger.warning("API Quota driven! Stopping collector.")
            return False
        return True

    def sync_teams_and_matches(self, league_id: int, season: int):
        """
        Fetch ALL matches for a season in 1 API call.
        Updates Teams and Matches in database.
        """
        if not self.check_quota():
            return

        logger.info(f"Fetching fixtures for League {league_id}, Season {season}...")
        fixtures = self.client.get_fixtures(league_id=league_id, season=season)
        
        if not fixtures:
            logger.warning("No fixtures found.")
            return

        logger.info(f"Found {len(fixtures)} matches. Syncing to database...")
        
        # 1. Sync Teams first (to avoid FK errors)
        self._sync_teams(fixtures)
        
        # 2. Sync Matches
        self._sync_matches(fixtures, league_id, season)
        
        logger.info("Sync complete!")

    def _sync_teams(self, fixtures: List[Dict]):
        """Extract and save unique teams"""
        seen_ids = set()
        
        for f in fixtures:
            for side in ["home", "away"]:
                team_data = f["teams"][side]
                t_id = team_data["id"]
                
                if t_id in seen_ids:
                    continue
                    
                seen_ids.add(t_id)
                
                # Check if exists
                existing = self.db.query(Team).filter(Team.api_id == str(t_id)).first()
                if not existing:
                    new_team = Team(
                        api_id=str(t_id),
                        name=team_data["name"],
                        country="Portugal", # Assuming Portugal for now
                        logo_url=team_data["logo"],
                        league="Primeira Liga"
                    )
                    self.db.add(new_team)
        
        self.db.commit()

    def _sync_matches(self, fixtures: List[Dict], league_id: int, season: int):
        """Save matches"""
        for f in fixtures:
            fixture_id = f["fixture"]["id"]
            
            # Find teams in DB
            home_team = self.db.query(Team).filter(Team.api_id == str(f["teams"]["home"]["id"])).first()
            away_team = self.db.query(Team).filter(Team.api_id == str(f["teams"]["away"]["id"])).first()
            
            if not home_team or not away_team:
                continue

            match_date = datetime.fromisoformat(f["fixture"]["date"].replace("Z", "+00:00"))
            status = f["fixture"]["status"]["short"]
            
            # Check if match exists
            # We don't have api_id on Match model yet, we normally should add it.
            # For now mapping by date and teams or we add api_id column to Match model (Recommended)
            
            # Let's verify our Match model structure first.
            # Assuming we might need to update Match model to store external API ID.
            # For this MVP, I'll assume we insert if not found by date+teams
            
            existing = self.db.query(Match).filter(
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
                Match.match_date == match_date
            ).first()

            if existing: # Update score if finished
                if status == "FT":
                    existing.home_score = f["goals"]["home"]
                    existing.away_score = f["goals"]["away"]
                    existing.status = "finished"
            else:
                new_match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    league="Primeira Liga", # Could be dynamic
                    season=str(season),     # Add season to model if not exists
                    status="finished" if status == "FT" else "scheduled",
                    home_score=f["goals"]["home"],
                    away_score=f["goals"]["away"]
                )
                self.db.add(new_match)
        
        self.db.commit()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run collector
    collector = FootballDataCollector()
    
    # Liga Portugal ID = 94
    # Fetch 2023 Season (Historical) - 1 Call
    collector.sync_teams_and_matches(league_id=94, season=2023)
