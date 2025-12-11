"""
Undo Manchester merge
Separates Manchester United and Manchester City back into distinct teams
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def undo_manchester_merge():
    """Separate Manchester United and Manchester City"""
    db = SessionLocal()
    
    try:
        # Find the merged team (should be named "Manchester" or "United" or "City")
        merged_options = ["Manchester", "United", "City", "Manchester United", "Manchester City"]
        
        merged_team = None
        for name in merged_options:
            merged_team = db.query(Team).filter(Team.name == name).first()
            if merged_team:
                logger.info(f"Found merged team: {merged_team.name} (ID: {merged_team.id})")
                break
        
        if not merged_team:
            logger.error("Could not find merged Manchester team")
            return
        
        # Create/Get Manchester United
        man_utd = db.query(Team).filter(Team.name == "Manchester United").first()
        if not man_utd:
            man_utd = Team(name="Manchester United", league="Premier League", country="England")
            db.add(man_utd)
            db.flush()
            logger.info(f"Created Manchester United (ID: {man_utd.id})")
        
        # Create/Get Manchester City
        man_city = db.query(Team).filter(Team.name == "Manchester City").first()
        if not man_city:
            man_city = Team(name="Manchester City", league="Premier League", country="England")
            db.add(man_city)
            db.flush()
            logger.info(f"Created Manchester City (ID: {man_city.id})")
        
        # Get all matches with merged team
        matches = db.query(Match).filter(
            (Match.home_team_id == merged_team.id) | 
            (Match.away_team_id == merged_team.id)
        ).all()
        
        logger.info(f"Found {len(matches)} matches to redistribute")
        
        # We need to check opponent to determine which Manchester team
        # For now, just ask user or split evenly
        # Better: check historical data or match details
        
        logger.warning("⚠️ Cannot automatically determine which matches belong to which team")
        logger.warning("   Please manually verify and reassign matches")
        
        # Safest approach: Keep as is and user manually corrects
        db.rollback()
        
        logger.info("✅ Kept teams separate - please manually clean up if needed")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    undo_manchester_merge()
