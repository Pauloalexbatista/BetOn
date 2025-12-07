
from fastapi import Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Match, Team

class MatchFilters:
    def __init__(
        self,
        league: Optional[str] = Query(None, description="Filter by League name"),
        season: Optional[str] = Query(None, description="Filter by Season (e.g. 2024/2025)"),
        team_id: Optional[int] = Query(None, description="Filter by Team ID"),
        team_name: Optional[str] = Query(None, description="Filter by Team Name"),
        round: Optional[str] = Query(None, description="Filter by Round (e.g., '5')"),
        start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    ):
        self.league = league
        self.season = season
        self.team_id = team_id
        self.team_name = team_name
        self.round = round
        self.start_date = start_date
        self.end_date = end_date

    def apply(self, query):
        if self.league:
            query = query.filter(Match.league == self.league)
        if self.season:
            query = query.filter(Match.season == self.season)
        if self.team_id:
            query = query.filter((Match.home_team_id == self.team_id) | (Match.away_team_id == self.team_id))
        if self.team_name:
            # Join with Team table to filter by name
            # We use distinct to avoid duplicates if a team plays itself (impossible) but good practice
            query = query.join(Team, (Match.home_team_id == Team.id) | (Match.away_team_id == Team.id))
            query = query.filter(Team.name == self.team_name)
        if self.round:
            query = query.filter(Match.round == self.round)
        if self.start_date:
            query = query.filter(Match.match_date >= self.start_date)
        if self.end_date:
            query = query.filter(Match.match_date <= self.end_date)
            
        return query

class BetFilters(MatchFilters):
    """
    Extends MatchFilters to apply to Bets by joining with Match table.
    """
    def apply(self, query):
        # Join with Match table is assumed to be done by the caller OR we do it here if not present?
        # Safer to assume caller joins Match, or we check.
        # But to be safe, let's just apply filters on the Match entity columns.
        
        # Note: distinct() might be needed if joining causes duplicates, but 1-to-1 bet-match relationship usually ok.
        
        from database.models import Bet
        
        # We need to ensure query is joined with Match. 
        # Since we can't easily check if joined, we assume the base query includes .join(Match).
        
        if self.league:
            query = query.filter(Match.league == self.league)
        if self.season:
            query = query.filter(Match.season == self.season)
        if self.team_id:
            query = query.filter((Match.home_team_id == self.team_id) | (Match.away_team_id == self.team_id))
        if self.start_date:
            query = query.filter(Match.match_date >= self.start_date)
        if self.end_date:
            query = query.filter(Match.match_date <= self.end_date)
            
        return query
