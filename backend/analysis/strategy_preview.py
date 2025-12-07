"""
Strategy Preview Engine
Lightweight simulation for quick strategy validation
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from datetime import datetime
import time

from database.models import Match, Team, Strategy


class StrategyPreviewEngine:
    """
    Quick preview engine for strategy validation
    Runs simplified backtest on recent matches
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_preview(
        self,
        conditions: List[Dict[str, Any]],
        target_outcome: str,
        leagues: List[str] = None,
        teams: List[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Run quick simulation on recent finished matches
        
        Args:
            conditions: List of strategy conditions
            target_outcome: Target bet outcome (home_win, btts_yes, etc.)
            leagues: Optional league filter
            teams: Optional team filter
            limit: Max matches to analyze (default 100)
        
        Returns:
            Dict with matches_found, win_rate, roi_estimate, sample_matches
        """
        start_time = time.time()
        
        # 1. Fetch recent finished matches
        query = self.db.query(Match).filter(
            Match.status == 'finished',
            Match.home_score.isnot(None),
            Match.away_score.isnot(None)
        )
        
        # Apply filters
        if leagues:
            query = query.filter(Match.league.in_(leagues))
        
        if teams:
            # Filter by team names
            team_ids = self.db.query(Team.id).filter(Team.name.in_(teams)).all()
            team_ids = [t[0] for t in team_ids]
            if team_ids:
                query = query.filter(
                    or_(
                        Match.home_team_id.in_(team_ids),
                        Match.away_team_id.in_(team_ids)
                    )
                )
        
        # Get recent matches
        matches = query.order_by(Match.match_date.desc()).limit(limit * 2).all()
        
        # 2. Evaluate which matches would trigger the strategy
        matched_matches = []
        
        for match in matches:
            # For preview, we use simplified evaluation
            # In real backtest, we'd check historical stats
            # Here we just check if match exists and has data
            if self._would_match_strategy(match, conditions):
                matched_matches.append(match)
                if len(matched_matches) >= limit:
                    break
        
        # 3. Calculate performance metrics
        if not matched_matches:
            return {
                "matches_found": 0,
                "win_rate": 0,
                "roi_estimate": 0,
                "total_profit": 0,
                "sample_matches": [],
                "execution_time_ms": round((time.time() - start_time) * 1000)
            }
        
        wins = 0
        total_profit = 0
        stake = 10  # Fixed stake for estimation
        
        sample_matches = []
        
        for match in matched_matches[:50]:  # Limit calculation to 50 for speed
            is_win = self._check_outcome(match, target_outcome)
            odds = self._estimate_odds(match, target_outcome)
            
            if is_win:
                wins += 1
                profit = (stake * odds) - stake
                total_profit += profit
            else:
                total_profit -= stake
            
            # Add to samples (first 5)
            if len(sample_matches) < 5:
                sample_matches.append({
                    "id": match.id,
                    "date": match.match_date.isoformat() if match.match_date else None,
                    "home": match.home_team.name if match.home_team else "Unknown",
                    "away": match.away_team.name if match.away_team else "Unknown",
                    "result": is_win,
                    "odds": round(odds, 2)
                })
        
        # Calculate metrics
        matches_evaluated = min(len(matched_matches), 50)
        win_rate = (wins / matches_evaluated * 100) if matches_evaluated > 0 else 0
        roi = (total_profit / (matches_evaluated * stake) * 100) if matches_evaluated > 0 else 0
        
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "matches_found": len(matched_matches),
            "win_rate": round(win_rate, 1),
            "roi_estimate": round(roi, 1),
            "total_profit": round(total_profit, 2),
            "sample_matches": sample_matches,
            "execution_time_ms": round(execution_time)
        }
    
    def _would_match_strategy(self, match: Match, conditions: List[Dict]) -> bool:
        """
        Simplified check if match would match strategy
        For preview, we accept all matches (full evaluation is expensive)
        In production, this would check historical team stats
        """
        # For MVP preview: accept all finished matches
        # TODO: Implement actual condition evaluation using historical stats
        return True
    
    def _check_outcome(self, match: Match, target_outcome: str) -> bool:
        """Check if the target outcome occurred in this match"""
        if not match.home_score or not match.away_score:
            return False
        
        home_score = match.home_score
        away_score = match.away_score
        total_goals = home_score + away_score
        
        outcome_map = {
            "home_win": home_score > away_score,
            "away_win": away_score > home_score,
            "draw": home_score == away_score,
            "over_2.5": total_goals > 2.5,
            "under_2.5": total_goals < 2.5,
            "over_1.5": total_goals > 1.5,
            "under_1.5": total_goals < 1.5,
            "btts_yes": home_score > 0 and away_score > 0,
            "btts_no": home_score == 0 or away_score == 0,
        }
        
        return outcome_map.get(target_outcome, False)
    
    def _estimate_odds(self, match: Match, target_outcome: str) -> float:
        """
        Estimate odds for the target outcome
        Uses match odds if available, otherwise estimates
        """
        # Try to get actual odds from match
        if match.odds and len(match.odds) > 0:
            for odd_entry in match.odds:
                if odd_entry.odds_data:
                    # Map target to odds key
                    odds_key_map = {
                        "home_win": "home",
                        "away_win": "away",
                        "draw": "draw",
                        "over_2.5": "over_2.5",
                        "under_2.5": "under_2.5",
                        "btts_yes": "btts_yes",
                        "btts_no": "btts_no"
                    }
                    
                    key = odds_key_map.get(target_outcome)
                    if key and key in odd_entry.odds_data:
                        return float(odd_entry.odds_data[key])
        
        # Fallback: estimate based on outcome type
        odds_estimates = {
            "home_win": 2.0,
            "away_win": 3.5,
            "draw": 3.2,
            "over_2.5": 1.85,
            "under_2.5": 2.0,
            "btts_yes": 1.75,
            "btts_no": 2.1
        }
        
        return odds_estimates.get(target_outcome, 2.0)
