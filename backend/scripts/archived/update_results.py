
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal, init_db
from collectors.football_data_co_uk import FootballDataCoUkCollector
from collectors.schedule_collector import ScheduleCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all():
    logger.info("🚀 Starting Daily Update Routine...")
    
    # 1. Update Results & Stats (Historical / Yesterday)
    # We fetch the current season files again. They are updated weekly/daily by the provider.
    logger.info("--- Step 1: Updating Results & Stats (football-data.co.uk) ---")
    try:
        results_collector = FootballDataCoUkCollector()
        # Sync only current season and maybe last season to be safe? 
        # Just current "2526" is usually enough for daily updates.
        results_collector.sync_season(target_season="2526") 
    except Exception as e:
        logger.error(f"Failed to update results: {e}")

    # 2. Update Schedule (Future)
    logger.info("--- Step 2: Updating Schedule (API-Football) ---")
    try:
        schedule_collector = ScheduleCollector()
        schedule_collector.sync_upcoming(days=14) # Get next 2 weeks
    except Exception as e:
        logger.error(f"Failed to update schedule: {e}")

    logger.info("✅ Update Routine Complete.")

if __name__ == "__main__":
    init_db() # Ensure DB exists
    update_all()
