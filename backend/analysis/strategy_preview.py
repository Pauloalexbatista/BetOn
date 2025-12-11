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
        stake = 10 # Default stake for simulation
        
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
                
                # EXCLUDE Head-to-Head matches (where BOTH teams are in the selected list)
                # This prevents "conflicts of interest" or betting on matches between two "Top" teams
                query = query.filter(
                    ~((Match.home_team_id.in_(team_ids)) & (Match.away_team_id.in_(team_ids)))
                )
        
        # Get recent matches
        # Increase limit significantly to find matches across many rounds
        # For accumulators, we need matches from different rounds
        matches = query.order_by(Match.match_date.desc()).limit(limit * 10).all()
        
        # 2. Evaluate which matches would trigger the strategy
        matched_matches = []
        
        for match in matches:
            # For preview, we use simplified evaluation
            # In real backtest, we'd check historical stats
            # Here we just check if match exists and has data
            if self._would_match_strategy(match, conditions):
                # Conflict Check: If both Home and Away are in selected teams, exclude?
                if teams and len(teams) > 1:
                    sel_teams = [t.lower().strip() for t in teams]
                    h_name = (match.home_team.name or "").lower().strip()
                    a_name = (match.away_team.name or "").lower().strip()
                    
                    if h_name in sel_teams and a_name in sel_teams:
                        # Skip H2H matches (both teams in selection)
                        continue
                     
                matched_matches.append(match)
                # For accumulators, don't limit too early - we need coverage across rounds
                if len(matched_matches) >= limit * 2:
                    break
        
        if not matched_matches:
             # If no historical matches found, we still want to check UPCOMING
             sample_matches = []
             wins = 0
             total_profit = 0
        else:
            # Process matches for metrics
            wins = 0
            total_profit = 0
            sample_matches = []
            
            for match in matched_matches:
                # We need to simulate the result
                # For finished matches, we know the result
                is_win = False
                
                # Get REAL odds from database
                odds = self._get_match_odds(match, target_outcome, teams)
                if odds == 0.0:
                    odds = 2.0  # Fallback if no odds found
                
                # Check outcome with team context for "win" target
                if target_outcome == 'win':
                    # For "win" target with selected teams, verify the selected team won
                    is_win = self._check_outcome_with_teams(match, target_outcome, teams)
                elif target_outcome == 'home_win':
                    is_win = match.home_score > match.away_score
                elif target_outcome == 'away_win':
                    is_win = match.away_score > match.home_score
                elif target_outcome == 'draw':
                    is_win = match.home_score == match.away_score
                else:
                    # For other targets (over/under, btts), use standard check
                    is_win = self._check_outcome(match, target_outcome)
                    
                if is_win:
                    wins += 1
                    total_profit += (stake * odds) - stake
                else:
                    total_profit -= stake
                    
                sample_matches.append({
                    "id": match.id,
                    "date": match.match_date.isoformat() if match.match_date else None,
                    "home": match.home_team.name,
                    "away": match.away_team.name,
                    "round": match.round,
                    "season": match.season,
                    "result": is_win,
                    "odds": round(odds, 2),
                    "ev": 0
                })

        # 3. Calculate performance metrics
        matches_evaluated = len(matched_matches)
        win_rate = (wins / matches_evaluated * 100) if matches_evaluated > 0 else 0
        roi = (total_profit / (matches_evaluated * stake) * 100) if matches_evaluated > 0 else 0
        
        # 4. Simulate Accumulators (Multiples)
        # Use ALL matches for accumulator simulation (not just first 50)
        accumulators = self._simulate_accumulators(sample_matches, target_outcome)
        
        # 5. [NEW] Get Upcoming Matches
        # Using the same conditions to find future opportunities
        upcoming_matches = self.get_upcoming_matches(
            conditions=conditions, 
            leagues=leagues, 
            teams=teams,
            target_outcome=target_outcome
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "matches_found": len(matched_matches),
            "win_rate": round(win_rate, 1),
            "roi_estimate": round(roi, 1),
            "total_profit": round(total_profit, 2),
            "sample_matches": sample_matches[:100], 
            "accumulators": accumulators,
            "upcoming_matches": upcoming_matches, # New field
            "execution_time_ms": round(execution_time)
        }

    def get_upcoming_matches(
        self,
        conditions: List[Dict[str, Any]],
        target_outcome: str,
        leagues: List[str] = None,
        teams: List[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Identify upcoming matches that fit the strategy criteria
        """
        # 1. Fetch Scheduled Matches (future only)
        from datetime import datetime
        now = datetime.utcnow()
        
        query = self.db.query(Match).filter(
            Match.status == 'scheduled',
            Match.match_date > now
        )
        
        if leagues:
            query = query.filter(Match.league.in_(leagues))
            
        if teams:
            team_ids = self.db.query(Team.id).filter(Team.name.in_(teams)).all()
            team_ids = [t[0] for t in team_ids]
            if team_ids:
                query = query.filter(
                    or_(
                        Match.home_team_id.in_(team_ids),
                        Match.away_team_id.in_(team_ids)
                    )
                )

        # Get next matches (increase multiplier to find more)
        matches = query.order_by(Match.match_date.asc()).limit(limit * 10).all()
        
        valid_upcoming = []
        for match in matches:
            # Conflict Check
            if teams and len(teams) > 1: # check if teams list is provided
                 # Normalize for comparison
                 sel_teams = [t.lower().strip() for t in teams]
                 home_name = (match.home_team.name or "").lower().strip()
                 away_name = (match.away_team.name or "").lower().strip()
                 
                 if home_name in sel_teams and away_name in sel_teams:
                     continue

            if self._would_match_strategy(match, conditions):
                # GET REAL ODDS from database
                odds = self._get_match_odds(match, target_outcome, teams)
                
                # If no odds found, use fallback average odds by market
                if odds == 0.0:
                    fallback_odds = {
                        'home_win': 1.8,
                        'away_win': 2.5,
                        'draw': 3.2,
                        'over_2.5': 1.9,
                        'under_2.5': 2.0,
                        'btts_yes': 2.1,
                        'win': 2.0  # Generic fallback
                    }
                    odds = fallback_odds.get(target_outcome, 2.0)
                
                valid_upcoming.append({
                    "id": match.id,
                    "date": match.match_date.isoformat() if match.match_date else None,
                    "home": match.home_team.name if match.home_team else "Unknown",
                    "away": match.away_team.name if match.away_team else "Unknown",
                    "round": match.round,
                    "season": match.season,
                    "odds": round(odds, 2),  # REAL ODDS
                    "result": None # Pending
                })
                if len(valid_upcoming) >= limit:
                    break
                    
        # Simulate Upcoming Accumulators (Potential)
        # We assume they are eligible bets
        simulated_accas = self._simulate_accumulators(
            valid_upcoming, 
            target_outcome, 
            leg_count=2 # Default to doubles
        )
        
        return {
            "matches": valid_upcoming,
            "accumulators": simulated_accas
        }
        
        wins = 0
        total_profit = 0
        stake = 10  # Fixed stake for estimation
        
        sample_matches = []
        
        for match in matched_matches[:50]:  # Limit calculation to 50 for speed
            is_win = self._check_outcome(match, target_outcome)
            
            # Get REAL odds from DB
            odds = self._get_match_odds(match, target_outcome)
            if odds == 0.0:
                odds = 1.0 # Avoid division by zero, but means no profit
            
            # Calculate EV (approximate probability based on win rate of this strategy so far? 
            # Or simplified: if we think this is a good strategy, we assume >50% prob? 
            # For now, let's calculate EV based on implied probability vs outcome? 
            # Actually, EV requires a probability model. 
            # Let's use a placeholder probability or the win rate of the strategy as a proxy?)
            # BETTER: Use the team's historical win rate as the 'true probability' estimate
            
            # Calculate EV based on historical form
            # We need to quickly fetch the team's win rate prior to this match
            # This is a bit inefficient (N+1 queries) but OK for preview (limited to 50)
            
            ev = 0.0
            prob = 0.0
            
            try:
                # Determine "primary" team for the outcome (e.g. Home team for Home Win)
                stats_team_id = None
                if target_outcome == "home_win" or target_outcome == "win":
                    stats_team_id = match.home_team_id
                elif target_outcome == "away_win":
                    stats_team_id = match.away_team_id
                
                if stats_team_id:
                     # Get last 5 games form
                    previous_matches = self.db.query(Match).filter(
                        Match.status == 'finished',
                        Match.match_date < match.match_date,
                        or_(
                            Match.home_team_id == stats_team_id,
                            Match.away_team_id == stats_team_id
                        )
                    ).order_by(Match.match_date.desc()).limit(10).all()
                    
                    if previous_matches:
                        wins = 0
                        for pm in previous_matches:
                            # Simplified: did they win?
                            is_home = pm.home_team_id == stats_team_id
                            p_home_win = pm.home_score > pm.away_score
                            p_away_win = pm.away_score > pm.home_score
                            
                            if (is_home and p_home_win) or (not is_home and p_away_win):
                                wins += 1
                        
                        prob = wins / len(previous_matches)
                        ev = (prob * odds) - 1.0
            except:
                pass # Fail silently on stats for speed

            if is_win:
                wins += 1
                profit = (stake * odds) - stake
                total_profit += profit
            else:
                total_profit -= stake
            
            # Add to samples (keep all for accumulator logic, but limit return to UI)
            # We need ALL matches to form proper accumulators, not just the first 5
            sample_matches.append({
                "id": match.id,
                "date": match.match_date.isoformat() if match.match_date else None,
                "home": match.home_team.name if match.home_team else "Unknown",
                "away": match.away_team.name if match.away_team else "Unknown",
                "round": match.round,
                "season": match.season,
                "result": is_win,
                "odds": round(odds, 2),
                "ev": round(ev, 2)
            })
        
        # Calculate metrics
        matches_evaluated = len(matched_matches)
        win_rate = (wins / matches_evaluated * 100) if matches_evaluated > 0 else 0
        roi = (total_profit / (matches_evaluated * stake) * 100) if matches_evaluated > 0 else 0
        
        # 4. Simulate Accumulators (Multiples)
        # We pass ALL matches to the simulator to find possible accas across history
        accumulators = self._simulate_accumulators(sample_matches, target_outcome)
        
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "matches_found": len(matched_matches),
            "win_rate": round(win_rate, 1),
            "roi_estimate": round(roi, 1),
            "total_profit": round(total_profit, 2),
            "sample_matches": sample_matches[:50], # Only return 50 for the list view to save bandwidth
            "accumulators": accumulators[:20], # Return top 20 recent accumulators
            "execution_time_ms": round(execution_time)
        }

    def _simulate_accumulators(self, single_bets: List[Dict], target_outcome: str, leg_count: int = 2) -> List[Dict]:
        """
        Simulate Accumulators grouped by Round (Jornada)
        FIXED: Consistent grouping by season+round, fallback to ISO week
        Constraints:
        - Same Season + Same Round
        - No conflicting matches (e.g. betting on Home Team AND Away Team in same match)
        """
        import logging
        logger = logging.getLogger(__name__)
       
        logger.info(f"📊 Accumulator Simulator: Processing {len(single_bets)} single bets")
        logger.info(f"   Target outcome: {target_outcome}, Leg count: {leg_count}")
        
        # Group by Season + Round (or ISO week as fallback)
        by_round = {}
        
        for bet in single_bets:
            # ALWAYS prioritize Season + Round when available
            if bet.get('season') and bet.get('round'):
                # Normalize season format (handle "2023/2024" or "2023-2024")
                season = str(bet['season']).strip().replace('/', '-')
                round_num = str(bet['round']).strip()
                key = f"{season}|R{round_num}"
            elif bet.get('date'):
                # Fallback: Group by ISO week
                # This ensures games in same week are grouped even without round info
                from datetime import datetime
                try:
                    # Handle ISO format with timezone
                    date_str = bet['date'].replace('Z', '+00:00')
                    date_obj = datetime.fromisoformat(date_str)
                    year, week, _ = date_obj.isocalendar()
                    key = f"{year}|W{week:02d}"
                except:
                    # Skip if date parsing fails
                    continue
            else:
                continue
                
            if key not in by_round:
                by_round[key] = []
            by_round[key].append(bet)
        
        logger.info(f"📦 Created {len(by_round)} round groups:")
        for key, bets in list(by_round.items())[:5]:  # Show first 5
            logger.info(f"   {key}: {len(bets)} bets")
            
        accas = []
        stake = 10
        
        # Create accas
        for key, bets in by_round.items():
            # Need at least 'leg_count' bets (or 2 for doubles)
            if len(bets) < 2:
                continue
                
            # Sort by EV (descending)
            bets.sort(key=lambda x: x.get('ev', -100), reverse=True)
            
            # Selection Logic with Conflict Resolution
            selection = []
            selected_match_ids = set()
            
            for bet in bets:
                if len(selection) >= leg_count:
                    break
                
                # Check conflict: Have we already picked this match?
                if bet['id'] in selected_match_ids:
                    continue # Skip conflicting bet in same match
                    
                selection.append(bet)
                selected_match_ids.add(bet['id'])
            
            if len(selection) < 2:
                continue
            
            # Calculate Combined Odds
            combined_odds = 1.0
            is_win = True
            
            for leg in selection:
                combined_odds *= leg['odds']
                if not leg.get('result', False):
                    is_win = False
            
            accas.append({
                "date": key, # Display "2023-2024|R15"
                "legs": len(selection),
                "combined_odds": round(combined_odds, 2),
                "is_win": is_win,
                "profit": round((stake * combined_odds - stake) if is_win else -stake, 2),
                "matches": selection
            })
            
        # Sort by "date" (string sort works for our format)
        accas.sort(key=lambda x: x['date'], reverse=True)
        
        logger.info(f"✅ Generated {len(accas)} accumulators")
        return accas
    
    def _map_metric(self, metric: str) -> str:
        """Map Portuguese metrics to internal keys"""
        if not metric: return metric
        m = metric.lower()
        if 'golos marcados' in m: return 'avg_goals_scored'
        if 'golos sofridos' in m: return 'avg_goals_conceded'
        if 'vitórias' in m or 'vitorias' in m: return 'wins' # Note: wins in stats is Total, but we might want rate? 
        # Actually stats dict has 'win_rate'. If user says "Vitórias > 50", they mean rate usually.
        # But if they say "Vitórias > 5" (count).
        # Let's support Rate if threshold > 1? Or just map to win_rate?
        # Usually strategies use %.
        if 'win rate' in m or 'taxa de vitória' in m: return 'win_rate'
        
        # Fallback to direct key
        return metric

    def _would_match_strategy(self, match: Match, conditions: List[Dict]) -> bool:
        """
        Check if match would match strategy conditions
        Evaluates historical team stats against strategy rules
        """
        # No conditions = accept all matches
        if not conditions or len(conditions) == 0:
            return True
        
        # Evaluate each condition
        for condition in conditions:
            entity = condition.get('entity', 'home_team')
            metric = condition.get('metric')
            operator = condition.get('operator')
            threshold = condition.get('value')
            last_n = condition.get('last_n_games', 5)
            
            # Map metric name
            mapped_metric = self._map_metric(metric)
            
            # Get team stats
            team_stats = self._get_team_historical_stats(match, entity, last_n)
            
            if not team_stats:
                return False  # No data = don't match
            
            # Get metric value
            metric_value = team_stats.get(mapped_metric, 0)
            
            # Evaluate condition
            if not self._evaluate_condition(metric_value, operator, threshold):
                return False  # Condition not met
                
        return True  # All conditions met
        
        return True  # All conditions met
    
    def _get_team_historical_stats(self, match: Match, entity: str, last_n: int) -> Dict[str, float]:
        """
        Calculate historical stats for a team before this match
        """
        # Determine which team to analyze
        # 'Team' defaults to home_team for now (simplification)
        if entity == 'home_team' or entity == 'Team':
            team_id = match.home_team_id
        elif entity == 'away_team':
            team_id = match.away_team_id
        else:
            return {}
        
        if not team_id:
            return {}
        
        # Get previous matches for this team (before current match date)
        previous_matches = self.db.query(Match).filter(
            Match.status == 'finished',
            Match.match_date < match.match_date,
            or_(
                Match.home_team_id == team_id,
                Match.away_team_id == team_id
            ),
            Match.home_score.isnot(None),
            Match.away_score.isnot(None)
        ).order_by(Match.match_date.desc()).limit(last_n).all()
        
        if not previous_matches:
            return {}
        
        # Calculate stats
        stats = {
            'goals_scored': 0,
            'goals_conceded': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'clean_sheets': 0,
            'btts': 0,
            'over_2.5': 0,
            'under_2.5': 0,
        }
        
        for prev_match in previous_matches:
            is_home = prev_match.home_team_id == team_id
            
            if is_home:
                goals_for = prev_match.home_score
                goals_against = prev_match.away_score
            else:
                goals_for = prev_match.away_score
                goals_against = prev_match.home_score
            
            stats['goals_scored'] += goals_for
            stats['goals_conceded'] += goals_against
            
            if goals_for > goals_against:
                stats['wins'] += 1
            elif goals_for == goals_against:
                stats['draws'] += 1
            else:
                stats['losses'] += 1
                
            if goals_against == 0:
                stats['clean_sheets'] += 1
                
            if goals_for + goals_against > 2.5:
                stats['over_2.5'] += 1
            else:
                stats['under_2.5'] += 1
                
            if goals_for > 0 and goals_against > 0:
                stats['btts'] += 1
        
        # Calculate Averages
        count = len(previous_matches)
        if count > 0:
            stats['avg_goals_scored'] = stats['goals_scored'] / count
            stats['avg_goals_conceded'] = stats['goals_conceded'] / count
        else:
            stats['avg_goals_scored'] = 0
            stats['avg_goals_conceded'] = 0
            
        # Calculate averages and percentages
        n_matches = len(previous_matches)
        return {
            'avg_goals_scored': stats['avg_goals_scored'],
            'avg_goals_conceded': stats['avg_goals_conceded'],
            'win_rate': (stats['wins'] / n_matches) * 100,
            'draw_rate': (stats['draws'] / n_matches) * 100,
            'loss_rate': (stats['losses'] / n_matches) * 100,
            'clean_sheet_rate': (stats['clean_sheets'] / n_matches) * 100,
            'btts_rate': (stats['btts'] / n_matches) * 100,
            'over_2.5_rate': (stats['over_2.5'] / n_matches) * 100,
            'under_2.5_rate': (stats['under_2.5'] / n_matches) * 100,
        }
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate a single condition"""
        operators = {
            '>': lambda v, t: v > t,
            '>=': lambda v, t: v >= t,
            '<': lambda v, t: v < t,
            '<=': lambda v, t: v <= t,
            '==': lambda v, t: abs(v - t) < 0.01,  # Float comparison
            '!=': lambda v, t: abs(v - t) >= 0.01,
        }
        
        eval_func = operators.get(operator)
        if not eval_func:
            return False
        
        return eval_func(value, threshold)
    
    def _check_outcome(self, match: Match, target_outcome: str) -> bool:
        """Check if the target outcome occurred in this match"""
        if match.home_score is None or match.away_score is None:
            return False
        
        home_score = match.home_score
        away_score = match.away_score
        total_goals = home_score + away_score
        
        outcome_map = {
            "win": home_score != away_score,  # Any win (home OR away)
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
    
    def _check_outcome_with_teams(self, match: Match, target_outcome: str, selected_teams: List[str]) -> bool:
        """
        Check if the target outcome occurred AND if the selected team won
        This is specifically for 'win' target when multiple teams are selected
        """
        if match.home_score is None or match.away_score is None:
            return False
        
        home_score = match.home_score
        away_score = match.away_score
        
        # No winner in a draw
        if home_score == away_score:
            return False
        
        # If no teams selected, fall back to standard check
        if not selected_teams:
            return self._check_outcome(match, target_outcome)
        
        # Normalize team names for comparison
        selected_teams_normalized = [t.lower().strip() for t in selected_teams]
        home_team_name = (match.home_team.name or "").lower().strip()
        away_team_name = (match.away_team.name or "").lower().strip()
        
        # Check if home team is selected and won
        if home_team_name in selected_teams_normalized and home_score > away_score:
            return True
        
        # Check if away team is selected and won
        if away_team_name in selected_teams_normalized and away_score > home_score:
            return True
        
        # Selected team didn't win (or lost)
        return False

    
    def _get_match_odds(self, match: Match, target_outcome: str, selected_teams: List[str] = None) -> float:
        """
        Get actual odds from database
        Prioritizes Bet365, then Avg, then distinct bookmakers
        
        For 'win' target, determines which team is selected and returns appropriate odds
        """
        if not match.odds:
            return 0.0
            
        # Preference order
        bookmakers = ['Bet365', 'Avg', 'Pinnacle', '1xBet', 'Unibet', 'Max']
        
        # Map target to odds key
        # target_outcome -> keys in odds_data column
        key_map = {
            "home_win": "home",
            "away_win": "away",
            "draw": "draw",
            "over_2.5": "over_2.5",
            "under_2.5": "under_2.5",
            "btts_yes": "btts_yes",
            "btts_no": "btts_no"
        }
        
        # Special handling for "win" target
        if target_outcome == "win":
            # Need to determine which team is selected
            if selected_teams:
                selected_teams_normalized = [t.lower().strip() for t in selected_teams]
                home_team_name = (match.home_team.name or "").lower().strip()
                away_team_name = (match.away_team.name or "").lower().strip()
                
                if home_team_name in selected_teams_normalized:
                    needed_key = "home"
                elif away_team_name in selected_teams_normalized:
                    needed_key = "away"
                else:
                    # Neither team is selected, shouldn't happen
                    return 0.0
            else:
                # No teams selected, use home as default
                needed_key = "home"
        else:
            needed_key = key_map.get(target_outcome)
            if not needed_key:
                return 0.0  # Unknown target
                
        selected_odd = 0.0
        
        # Try to find preferred bookmaker
        for bookie in bookmakers:
            for odd_record in match.odds:
                if odd_record.bookmaker == bookie and odd_record.odds_data:
                    # Parse JSON if it's string (sqlalchemy sometimes returns dict, sometimes string depending on driver)
                    data = odd_record.odds_data
                    if isinstance(data, str):
                        import json
                        try:
                            data = json.loads(data)
                        except:
                            continue
                            
                    if needed_key in data:
                        try:
                            return float(data[needed_key])
                        except:
                            pass
                            
        # If no preferred found, take first available
        for odd_record in match.odds:
            if odd_record.odds_data:
                data = odd_record.odds_data
                if isinstance(data, str):
                    import json
                    try:
                        data = json.loads(data)
                    except:
                        continue
                if needed_key in data:
                    try:
                        return float(data[needed_key])
                    except:
                        pass
                        
        return 0.0

    def _calculate_ev(self, win_probability: float, odds: float) -> float:
        """
        Calculate Expected Value (EV)
        EV = (Probability * Odds) - 1
        """
        if odds <= 1.0: return -1.0
        return (win_probability * odds) - 1.0
