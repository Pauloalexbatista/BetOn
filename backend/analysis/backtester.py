from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import logging

from database.models import Match, Strategy, Team
from database.database import engine

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, db: Session):
        self.db = db

    def _get_match_odds(self, match: Match, target: str) -> float:
        """Fetch odds for the match target from DB"""
        # Targets: home_win, away_win, draw, over_2.5, under_2.5, btts_yes
        # 1. Try to find odds in match.odds relationship
        # We assume match has 'odds' loaded or we access attributes
        
        # Priority: Bet365 -> Pinnacle -> Avg
        # We need to map target to JSON key
        
        key_map = {
            "home_win": "home",
            "away_win": "away",
            "draw": "draw",
            "over_2.5": "over_2.5", # Assuming standard keys
            "under_2.5": "under_2.5",
            "btts_yes": "btts_yes",
            "btts_no": "btts_no"
        }
        
        json_key = key_map.get(target)
        if not json_key: 
            return 2.0 # Fallback if unknown target
            
        # Iterate odds available
        # Note: Match.odds is a relationship list
        best_odds = None
        
        for odd_entry in match.odds:
            # We look for market type matching the target
            # For 1x2, market="1x2". For goals, market="over_under"?
            # Simplification: FootballDataCoUk stores 1x2 properly.
            # Goals odds not always present in basic scrape
            
            data = odd_entry.odds_data
            if not data: continue
            
            # NOTE: Odds data stored by live_odds_collector from The Odds API
            val = data.get(json_key)
            if val:
                return float(val)
                
        return 1.90 # Default conservative odd if missing (better than 2.0)

    def run(self, strategy_id: int):
        """Run backtest for a specific strategy"""
        strategy = self.db.query(Strategy).get(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")
        
        logger.info(f"Running Backtest for: {strategy.name}")
        
        # 1. Fetch All Match History (Optimized: Load into memory/Pandas for speed)
        # We need matches with results to verify
        # We also need previous matches for "Last N Games" calculation
        
        # For simplicity MVP: Query all finished matches ordered by date
        # In production: Use Pandas for vectorization
        from sqlalchemy.orm import joinedload
        all_matches = self.db.query(Match).options(joinedload(Match.odds)).filter(
            Match.status == 'finished',
            Match.home_score.isnot(None)
        ).order_by(Match.match_date).all()
        
        results = []
        bankroll = 1000  # Starting Bankroll
        stake = 10 # Flat stake
        
        # Index matches by Team for fast "Last N" lookup
        team_matches = {} # {team_id: [match1, match2]}
        
        for match in all_matches:
            # Update history index before processing (simulation real-time)
            # Actually, we need to process chronology.
            
            # Check if this match triggers a bet
            if self._evaluate_strategy(strategy, match, team_matches):
                # Place Bet logic (Simulation)
                is_win = self._check_bet_result(strategy, match)
                
                # Get Odds (Real)
                odds_val = self._get_match_odds(match, strategy.target_outcome)
                
                # Calculate Profit
                if is_win:
                    profit = (stake * odds_val) - stake
                    # Note: We assume static stake.
                else:
                    profit = -stake
                
                bankroll += profit
                results.append({
                    "match_id": match.id,
                    "date": match.match_date,
                    "home": match.home_team.name,
                    "away": match.away_team.name,
                    "target": strategy.target_outcome,
                    "odds": odds_val,
                    "result": is_win,
                    "profit": profit,
                    "bankroll": bankroll
                })
            
            # Add to history AFTER evaluation (so we don't look ahead)
            self._add_to_history(team_matches, match)

        return results

    def _evaluate_strategy(self, strategy: Strategy, match: Match, team_matches: Dict[int, List[Match]]) -> bool:
        """Check if all conditions are met for this match"""
        for condition in strategy.conditions:
            
            # Determine Team Context
            target_team_id = match.home_team_id if condition.entity == 'home_team' else match.away_team_id
            
            # Get History
            history = team_matches.get(target_team_id, [])
            
            # Filter Context (Home/Away games only?)
            if condition.context == 'home':
                history = [m for m in history if m.home_team_id == target_team_id]
            elif condition.context == 'away':
                history = [m for m in history if m.away_team_id == target_team_id]
            
            # Slice Last N
            history = history[-condition.last_n_games:]
            
            if len(history) < condition.last_n_games:
                return False # Not enough data
            
            # Calculate Metric
            value = self._calculate_metric(condition.metric, history, target_team_id)
            
            # Compare
            if not self._compare(value, condition.operator, condition.value):
                return False
                
        return True

    def _calculate_metric(self, metric: str, history: List[Match], team_id: int) -> float:
        if not history: return 0
        
        if metric == 'goals_scored':
            goals = sum([m.home_score if m.home_team_id == team_id else m.away_score for m in history])
            return goals / len(history)
            
        if metric == 'goals_conceded':
            goals = sum([m.away_score if m.home_team_id == team_id else m.home_score for m in history])
            return goals / len(history)
            
        if metric == 'win_rate':
            wins = 0
            for m in history:
                is_home = m.home_team_id == team_id
                if is_home and m.home_score > m.away_score: wins += 1
                elif not is_home and m.away_score > m.home_score: wins += 1
            return (wins / len(history)) * 100
            
        return 0

    def _compare(self, actual, operator, target) -> bool:
        if operator == '>': return actual > target
        if operator == '<': return actual < target
        if operator == '=': return actual == target
        return False

    def _add_to_history(self, team_matches, match):
        if match.home_team_id not in team_matches: team_matches[match.home_team_id] = []
        if match.away_team_id not in team_matches: team_matches[match.away_team_id] = []
        
        team_matches[match.home_team_id].append(match)
        team_matches[match.away_team_id].append(match)

    def _check_bet_result(self, strategy, match):
        """Check if the bet won based on strategy target"""
        target = strategy.target_outcome
        
        home = match.home_score
        away = match.away_score
        total_goals = home + away
        
        if target == 'home_win':
            return home > away
        if target == 'away_win':
            return away > home
        if target == 'draw':
            return home == away
        if target == 'over_2.5':
            return total_goals > 2.5
        if target == 'under_2.5':
            return total_goals < 2.5
        if target == 'btts_yes':
            return home > 0 and away > 0
        if target == 'btts_no':
            return home == 0 or away == 0
            
        return False
