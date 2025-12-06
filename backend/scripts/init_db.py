"""
Database initialization script

This script initializes the SQLite database with:
- All tables
- Sample data for testing
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.database import init_db, SessionLocal
from database.models import Team, Match, Strategy, BankrollHistory
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create sample teams
        teams_data = [
            {"api_id": 1, "name": "FC Porto", "country": "Portugal", "league": "Primeira Liga"},
            {"api_id": 2, "name": "SL Benfica", "country": "Portugal", "league": "Primeira Liga"},
            {"api_id": 3, "name": "Sporting CP", "country": "Portugal", "league": "Primeira Liga"},
            {"api_id": 4, "name": "SC Braga", "country": "Portugal", "league": "Primeira Liga"},
        ]
        
        teams = []
        for team_data in teams_data:
            team = Team(**team_data)
            db.add(team)
            teams.append(team)
        
        db.commit()
        logger.info(f"Created {len(teams)} sample teams")
        
        # Create sample matches
        base_date = datetime.utcnow() + timedelta(days=1)
        matches_data = [
            {
                "api_id": 101,
                "home_team_id": teams[0].id,
                "away_team_id": teams[1].id,
                "league": "Primeira Liga",
                "season": "2024/2025",
                "match_date": base_date,
                "status": "scheduled"
            },
            {
                "api_id": 102,
                "home_team_id": teams[2].id,
                "away_team_id": teams[3].id,
                "league": "Primeira Liga",
                "season": "2024/2025",
                "match_date": base_date + timedelta(days=1),
                "status": "scheduled"
            }
        ]
        
        for match_data in matches_data:
            match = Match(**match_data)
            db.add(match)
        
        db.commit()
        logger.info(f"Created {len(matches_data)} sample matches")
        
        # Create sample strategies
        strategies_data = [
            {
                "name": "Value Betting",
                "description": "Bet when odds provide value above 5% edge",
                "strategy_type": "value_betting",
                "config": {"min_edge": 5.0, "max_stake_pct": 3.0},
                "is_active": False
            },
            {
                "name": "Form Based",
                "description": "Bet on teams in good form",
                "strategy_type": "form_based",
                "config": {"min_form_games": 5, "min_win_rate": 60.0},
                "is_active": False
            }
        ]
        
        for strategy_data in strategies_data:
            strategy = Strategy(**strategy_data)
            db.add(strategy)
        
        db.commit()
        logger.info(f"Created {len(strategies_data)} sample strategies")
        
        # Initialize bankroll
        initial_bankroll = BankrollHistory(
            balance=1000.0,
            change=1000.0,
            reason="initial_deposit",
            notes="Initial bankroll setup"
        )
        db.add(initial_bankroll)
        db.commit()
        logger.info("Initialized bankroll with €1000")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    logger.info("Initializing BetOn database...")
    
    # Create all tables
    init_db()
    logger.info("Database tables created successfully")
    
    # Create sample data
    create_sample_data()
    
    logger.info("Database initialization complete!")
    logger.info("You can now start the API server with: uvicorn main:app --reload")


if __name__ == "__main__":
    main()
