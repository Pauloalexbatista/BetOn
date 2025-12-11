"""
Reset Recent Odds Collection
Removes teams and matches created today, keeping historical data intact.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match, Odds
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_recent_data():
    """Remove teams and matches created recently"""
    db = SessionLocal()
    
    try:
        # Define cutoff (keep data older than 3 hours ago)
        cutoff = datetime.utcnow() - timedelta(hours=3)
        
        logger.info(f"Removing data created after: {cutoff}")
        
        # Get teams created recently
        recent_teams = db.query(Team).filter(Team.created_at > cutoff).all()
        recent_team_ids = [t.id for t in recent_teams]
        
        logger.info(f"Found {len(recent_teams)} recent teams to remove")
        
        # Get matches involving these teams
        recent_matches = db.query(Match).filter(
            (Match.home_team_id.in_(recent_team_ids)) |
            (Match.away_team_id.in_(recent_team_ids))
        ).all()
        
        logger.info(f"Found {len(recent_matches)} matches to remove")
        
        # Get odds for these matches
        match_ids = [m.id for m in recent_matches]
        recent_odds = db.query(Odds).filter(
            Odds.match_id.in_(match_ids)
        ).count() if match_ids else 0
        
        logger.info(f"Found {recent_odds} odds records to remove")
        
        # Delete in correct order (foreign keys)
        if match_ids:
            db.query(Odds).filter(Odds.match_id.in_(match_ids)).delete(synchronize_session=False)
            logger.info(f"✅ Deleted {recent_odds} odds")
        
        db.query(Match).filter(Match.id.in_(match_ids)).delete(synchronize_session=False)
        logger.info(f"✅ Deleted {len(recent_matches)} matches")
        
        db.query(Team).filter(Team.id.in_(recent_team_ids)).delete(synchronize_session=False)
        logger.info(f"✅ Deleted {len(recent_teams)} teams")
        
        db.commit()
        
        logger.info("\n✅ Reset Complete!")
        logger.info(f"   Removed: {len(recent_teams)} teams, {len(recent_matches)} matches, {recent_odds} odds")
        logger.info(f"   Historical data preserved")
        
        return len(recent_teams)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("RESET RECENT DATA")
    print("="*60)
    
    confirm = input("\n⚠️  Remove teams/matches created in last 3 hours? (yes/no): ")
    
    if confirm.lower() == "yes":
        reset_recent_data()
        print("\n✅ Done! You can now re-run the odds collector.")
    else:
        print("❌ Cancelled")
