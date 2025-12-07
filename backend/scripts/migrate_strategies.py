"""
Database Migration Script: Add missing columns to strategies table
Adds 'leagues' and 'teams' JSON columns to the strategies table.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_strategies_table():
    """Add missing columns to strategies table"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(strategies)"))
            columns = [row[1] for row in result]
            
            logger.info(f"Current columns in strategies table: {columns}")
            
            # Add leagues column if missing
            if 'leagues' not in columns:
                logger.info("Adding 'leagues' column...")
                conn.execute(text("ALTER TABLE strategies ADD COLUMN leagues JSON"))
                conn.commit()
                logger.info("✅ Added 'leagues' column")
            else:
                logger.info("✅ 'leagues' column already exists")
            
            # Add teams column if missing
            if 'teams' not in columns:
                logger.info("Adding 'teams' column...")
                conn.execute(text("ALTER TABLE strategies ADD COLUMN teams JSON"))
                conn.commit()
                logger.info("✅ Added 'teams' column")
            else:
                logger.info("✅ 'teams' column already exists")
            
            logger.info("\n✅ Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise


if __name__ == "__main__":
    try:
        migrate_strategies_table()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
