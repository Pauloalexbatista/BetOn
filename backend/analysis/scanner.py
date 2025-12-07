from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from database.models import Match, Strategy
from analysis.backtester import Backtester

logger = logging.getLogger(__name__)

class SignalScanner:
    def __init__(self, db: Session):
        self.db = db
        self.engine = Backtester(db) # Reuse logic

    def scan(self, hours_ahead=48):
        """Scan for opportunities in the next N hours"""
        logger.info(f"Scanning for signals next {hours_ahead}h...")
        
        # 1. Get Future Matches
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=hours_ahead)
        
        future_matches = self.db.query(Match).filter(
            Match.match_date >= start_time,
            Match.match_date <= end_time
            # Status could be 'scheduled' or 'timed'
        ).all()
        
        if not future_matches:
            logger.info("No future matches found.")
            return []

        # 2. Get Active Strategies
        strategies = self.db.query(Strategy).filter(Strategy.is_active == True).all()
        if not strategies:
            logger.info("No active strategies.")
            return []

        # 3. Pre-load History (Optimization)
        # For the scanner, we need the history of the TEAMS involved in future matches.
        # We can reuse the Backtester's logic but we need to feed it the 'team_matches' history.
        
        # Fetch all finished matches for context (Heavy query? dependent on DB size)
        # For MVP: Load all finished matches. 
        # Production: Load only matches for relevant teams.
        history_matches = self.db.query(Match).filter(
            Match.status == 'finished',
            Match.home_score.isnot(None)
        ).order_by(Match.match_date).all()
        
        # Build Index
        team_matches = {}
        for m in history_matches:
            self._add_to_history(team_matches, m)
            
        signals = []
        
        # 4. Evaluate
        for match in future_matches:
            for strat in strategies:
                # We reuse the Backtester's private method _evaluate_strategy
                # It expects (strategy, match, team_matches_history)
                if self.engine._evaluate_strategy(strat, match, team_matches):
                    signals.append({
                        "match_id": match.id,
                        "match_date": match.match_date,
                        "home_team": match.home_team.name,
                        "away_team": match.away_team.name,
                        "league": match.league,
                        "strategy_id": strat.id,
                        "strategy_name": strat.name,
                        "target_outcome": strat.target_outcome,
                        "confidence": "High" # Placeholder
                    })
                    
        return signals

    def _add_to_history(self, team_matches, match):
        if match.home_team_id not in team_matches: team_matches[match.home_team_id] = []
        if match.away_team_id not in team_matches: team_matches[match.away_team_id] = []
        
        team_matches[match.home_team_id].append(match)
        team_matches[match.away_team_id].append(match)
