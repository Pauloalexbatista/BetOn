"""
BetOn Health Check Script
Verifies database connectivity, data availability, and API configuration.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from config import get_settings
from database.models import Team, Match, Odds, Strategy, Bet, BankrollHistory
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_database_connection():
    """Check if database is accessible"""
    settings = get_settings()
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection: SUCCESS")
        return True, engine
    except Exception as e:
        logger.error(f"❌ Database connection: FAILED - {e}")
        return False, None


def check_tables_exist(engine):
    """Check if all required tables exist"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = ['teams', 'matches', 'odds', 'strategies', 'bets', 'bankroll_history']
    
    logger.info(f"\n📋 Database Tables ({len(tables)} found):")
    all_exist = True
    for table in required_tables:
        exists = table in tables
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {table}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_data_counts(engine):
    """Count records in each table"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        counts = {
            'Teams': db.query(Team).count(),
            'Matches': db.query(Match).count(),
            'Finished Matches': db.query(Match).filter(Match.status == 'finished').count(),
            'Scheduled Matches': db.query(Match).filter(Match.status == 'scheduled').count(),
            'Odds Records': db.query(Odds).count(),
            'Strategies': db.query(Strategy).count(),
            'Bets': db.query(Bet).count(),
            'Bankroll History': db.query(BankrollHistory).count(),
        }
        
        logger.info("\n📊 Data Counts:")
        has_data = False
        for name, count in counts.items():
            status = "✅" if count > 0 else "⚠️"
            logger.info(f"  {status} {name}: {count}")
            if count > 0:
                has_data = True
        
        if not has_data:
            logger.warning("\n⚠️  WARNING: Database is empty! Run data collectors to populate.")
        
        return counts
    finally:
        db.close()


def check_api_configuration():
    """Check if API keys are configured"""
    settings = get_settings()
    
    logger.info("\n🔑 API Configuration:")
    
    # API-Football
    api_football_configured = (
        settings.api_football_key and 
        settings.api_football_key != "" and 
        settings.api_football_key != "your_api_football_key"
    )
    status = "✅" if api_football_configured else "⚠️"
    logger.info(f"  {status} API-Football: {'Configured' if api_football_configured else 'NOT configured'}")
    
    # The Odds API
    odds_api_configured = (
        settings.the_odds_api_key and 
        settings.the_odds_api_key != "" and 
        settings.the_odds_api_key != "your_theodds_api_key"
    )
    status = "✅" if odds_api_configured else "⚠️"
    logger.info(f"  {status} The Odds API: {'Configured' if odds_api_configured else 'NOT configured'}")
    
    return {
        'api_football': api_football_configured,
        'the_odds_api': odds_api_configured
    }


def check_application_settings():
    """Display current application settings"""
    settings = get_settings()
    
    logger.info("\n⚙️  Application Settings:")
    logger.info(f"  • Paper Trading Mode: {settings.paper_trading_mode}")
    logger.info(f"  • Auto Bet Enabled: {settings.auto_bet_enabled}")
    logger.info(f"  • Initial Bankroll: €{settings.initial_bankroll}")
    logger.info(f"  • Max Stake %: {settings.max_stake_percentage}%")
    logger.info(f"  • Stop Loss %: {settings.stop_loss_percentage}%")


def main():
    """Run all health checks"""
    logger.info("=" * 60)
    logger.info("🏥 BetOn Health Check")
    logger.info("=" * 60)
    
    # 1. Database Connection
    db_ok, engine = check_database_connection()
    if not db_ok:
        logger.error("\n❌ CRITICAL: Cannot connect to database. Check DATABASE_URL in .env")
        return False
    
    # 2. Tables
    tables_ok = check_tables_exist(engine)
    if not tables_ok:
        logger.error("\n❌ CRITICAL: Missing required tables. Run: python scripts/init_db.py")
        return False
    
    # 3. Data Counts
    counts = check_data_counts(engine)
    
    # 4. API Configuration
    api_config = check_api_configuration()
    
    # 5. Application Settings
    check_application_settings()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📝 SUMMARY")
    logger.info("=" * 60)
    
    if counts['Matches'] == 0:
        logger.warning("⚠️  Database is empty. To populate data:")
        logger.info("   1. Configure API keys in .env")
        logger.info("   2. Run: python collectors/football_data_co_uk.py")
        logger.info("   3. Or run: python reset_and_load.py")
    else:
        logger.info("✅ System is healthy and ready to use!")
    
    if not api_config['api_football'] and not api_config['the_odds_api']:
        logger.warning("⚠️  No API keys configured. Live data collection disabled.")
    
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
