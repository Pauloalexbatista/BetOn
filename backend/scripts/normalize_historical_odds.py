"""
Normalize Historical Odds
Sets all existing odds to neutral value (1.30) for past matches.
This provides a baseline for historical data without relying on unreliable aggregated odds.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Odds, Match
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_historical_odds():
    """
    Set all odds for finished matches to neutral value 1.30
    This removes unreliable "Avg/Max" aggregations while keeping data structure intact.
    """
    db = SessionLocal()
    
    try:
        # Get all finished matches
        finished_matches = db.query(Match).filter(Match.status == "finished").all()
        finished_match_ids = [m.id for m in finished_matches]
        
        logger.info(f"Found {len(finished_match_ids)} finished matches")
        
        # Get all odds for finished matches
        historical_odds = db.query(Odds).filter(Odds.match_id.in_(finished_match_ids)).all()
        logger.info(f"Found {len(historical_odds)} historical odds records to normalize")
        
        # Normalize each odds record
        count = 0
        neutral_odds = {
            "home": 1.30,
            "draw": 1.30,
            "away": 1.30
        }
        
        for odd in historical_odds:
            # Update to neutral odds
            odd.odds_data = neutral_odds
            odd.bookmaker = "neutral"  # Mark as normalized
            odd.market = "1x2"
            count += 1
            
            if count % 1000 == 0:
                logger.info(f"  Processed {count} odds...")
        
        db.commit()
        logger.info(f"✅ Successfully normalized {count} historical odds to 1.30")
        
        # Summary
        remaining = db.query(Odds).filter(~Odds.match_id.in_(finished_match_ids)).count()
        logger.info(f"📊 Summary:")
        logger.info(f"   - Historical odds (normalized): {count}")
        logger.info(f"   - Current/future odds (unchanged): {remaining}")
        
        return count
        
    except Exception as e:
        logger.error(f"❌ Error normalizing odds: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_normalization():
    """Verify normalization was successful"""
    db = SessionLocal()
    
    try:
        # Check sample
        sample = db.query(Odds).filter(Odds.bookmaker == "neutral").limit(5).all()
        
        logger.info("\n🔍 Verification - Sample normalized odds:")
        for odd in sample:
            logger.info(f"   ID {odd.id}: {odd.market} | {odd.odds_data}")
        
        # Count by bookmaker
        from sqlalchemy import func
        by_bookmaker = db.query(
            Odds.bookmaker, 
            func.count(Odds.id)
        ).group_by(Odds.bookmaker).all()
        
        logger.info("\n📊 Odds by bookmaker after normalization:")
        for bookmaker, count in by_bookmaker:
            logger.info(f"   {bookmaker}: {count}")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("NORMALIZING HISTORICAL ODDS TO 1.30")
    print("="*60)
    
    confirm = input("\n⚠️  This will modify all odds for finished matches. Continue? (yes/no): ")
    
    if confirm.lower() == "yes":
        count = normalize_historical_odds()
        verify_normalization()
        print(f"\n✅ Done! Normalized {count} odds to 1.30")
    else:
        print("❌ Cancelled")
