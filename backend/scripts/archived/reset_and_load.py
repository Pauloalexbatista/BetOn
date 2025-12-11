import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import engine, Base, init_db
from collectors.football_data_collector import FootballDataCollector
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_and_load():
    settings = get_settings()
    
    if not settings.api_football_key:
        logger.error("API_FOOTBALL_KEY is missing in .env or config!")
        # Attempt to prompt or just fail? For automation, we fail.
        return

    logger.info("⚠️  DELETING ALL DATA... ⚠️")
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    logger.info("Database cleared.")

    # Re-create tables
    init_db()
    logger.info("Tables recreated.")

    # Run Collector
    logger.info("Starting Data Collection (Football-Data.co.uk)...")
    
    # Import new collector
    from collectors.football_data_co_uk import FootballDataCoUkCollector
    collector = FootballDataCoUkCollector()
    
    # Sync History (Last 3 Years for All Configured Leagues)
    # This covers: Portugal, England, Spain, Italy, Germany, France
    # Seasons: 25/26, 24/25, 23/24
    
    logger.info("Syncing History (Last 3 Years)...")
    collector.sync_history(years=3)

if __name__ == "__main__":
    reset_and_load()
