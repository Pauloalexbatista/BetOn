
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import List, Dict, Optional
from database.models import Match, Team

class StandingsEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_table(self, league: str, season: str, as_of_date: Optional[date] = None) -> List[Dict]:
        """
        Calculate league table for a specific season up to a specific date.
        """
        # 1. Get Matches
        query = self.db.query(Match).filter(
            Match.league == league,
            Match.season == season,
            Match.status == "finished"
        )
        
        if as_of_date:
            query = query.filter(Match.match_date <= as_of_date)
            
        matches = query.all()
        
        # 2. Process Table
        table = {} # team_id -> Stats
        
        for m in matches:
            self._update_team_stats(table, m.home_team_id, m.home_score, m.away_score, is_home=True)
            self._update_team_stats(table, m.away_team_id, m.away_score, m.home_score, is_home=False)
            
        # 3. Enrich with Team Details
        results = []
        for team_id, stats in table.items():
            team = self.db.query(Team).get(team_id)
            if not team: continue
            
            stats["team"] = team.name
            stats["team_id"] = team.id
            stats["logo"] = team.logo_url
            stats["gd"] = stats["gf"] - stats["ga"]
            results.append(stats)
            
        # 4. Sort (Points, GD, GF)
        results.sort(key=lambda x: (x["points"], x["gd"], x["gf"]), reverse=True)
        
        # 5. Add Position
        for i, row in enumerate(results):
            row["position"] = i + 1
            
        return results

    def _update_team_stats(self, table, team_id, goals_for, goals_against, is_home):
        if team_id not in table:
            table[team_id] = {
                "played": 0, "won": 0, "drawn": 0, "lost": 0,
                "gf": 0, "ga": 0, "points": 0
            }
            
        stats = table[team_id]
        stats["played"] += 1
        stats["gf"] += goals_for
        stats["ga"] += goals_against
        
        if goals_for > goals_against:
            stats["won"] += 1
            stats["points"] += 3
        elif goals_for == goals_against:
            stats["drawn"] += 1
            stats["points"] += 1
        else:
            stats["lost"] += 1

    def get_team_position(self, team_id: int, league: str, season: str, as_of_date: date) -> int:
        """
        Get the position of a specific team at a specific date.
        Returns 0 if not found/no games.
        """
        # Optimization: We calculate the whole table. 
        # Caching could be used here in future (e.g. @lru_cache)
        table = self.calculate_table(league, season, as_of_date)
        
        for row in table:
            if row["team_id"] == team_id:
                return row["position"]
        return 0
