from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database.database import get_db
from database.models import Match
from api.filters import MatchFilters, Team
from pydantic import BaseModel

router = APIRouter()


class TeamResponse(BaseModel):
    id: int
    name: str
    country: str | None
    league: str | None
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    home_team: TeamResponse
    away_team: TeamResponse
    league: str
    match_date: datetime
    status: str
    home_score: int | None
    away_score: int | None
    
    # Odds (Optional/Flattened)
    home_odds: float | None = None
    draw_odds: float | None = None
    away_odds: float | None = None
    
    # Context (Calculated)
    round_calculated: int | None = None
    home_position: int | None = None
    away_position: int | None = None
    
    class Config:
        from_attributes = True


@router.get("/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    days: int = 7,
    league: str | None = None,
    db: Session = Depends(get_db)
):
    """Get upcoming matches for the next N days"""
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days)
    
    query = db.query(Match).filter(
        Match.match_date >= start_date,
        Match.match_date <= end_date,
        Match.status == "scheduled"
    )
    
    if league:
        query = query.filter(Match.league == league)
    
    matches = query.order_by(Match.match_date).all()
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match details by ID"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    skip: int = 0,
    limit: int = 50,
    filters: MatchFilters = Depends(),
    db: Session = Depends(get_db)
):
    """Get all matches with pagination and filters"""
    from sqlalchemy.orm import joinedload
    from database.models import Match # ensure visibility
    
    query = db.query(Match).options(joinedload(Match.odds))
    query = filters.apply(query)
    
    matches = query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()
    
    # Process matches to flatten odds (e.g. AvgH, AvgD, AvgA or Bet365)
    from analysis.standings import StandingsEngine
    engine = StandingsEngine(db)
    
    result = []
    for m in matches:
        # Clone attributes
        # We need to construct MatchResponse manually or let Pydantic handle it if we modify the object
        # Since 'matches' are simple ORM objects, we can inject attributes temporarily
        
        h_odd, d_odd, a_odd = None, None, None
        
        if m.odds:
            # Prefer Pinnacle then Bet365 then Avg
            preferred = ["Pinnacle", "Bet365", "Avg"]
            found = False
            for pref in preferred:
                for o in m.odds:
                    if o.bookmaker == pref and o.odds_data:
                        h_odd = o.odds_data.get("home")
                        d_odd = o.odds_data.get("draw")
                        a_odd = o.odds_data.get("away")
                        found = True
                        break
                if found: break
                
        # Inject into object (Pydantic will read these)
        m.home_odds = h_odd
        m.draw_odds = d_odd
        m.away_odds = a_odd
        
        # Calculate Context (Round & Position)
        # Note: This N+1 query pattern is slow. 
        # For MVP it's acceptable. For prod, we need bulk calculation.
        
        # Round: Count games for home team before this date + 1
        # m.round might be present from DB (if v3), if so use it.
        # If not (e.g. old data), calculate.
        
        if m.round:
            m.round_calculated = int(m.round) if m.round.isdigit() else 0
        else:
            # Calc
            past_games = db.query(Match).filter(
                Match.home_team_id == m.home_team_id,
                Match.season == m.season,
                Match.match_date < m.match_date
            ).count()
            m.round_calculated = past_games + 1
            
        # Position (Time Travel)
        # We use previous day to get standings ENTERING the match
        from datetime import timedelta
        prev_day = m.match_date.date() - timedelta(days=1)
        
        # Only calc for finished matches to avoid calculating future table constantly? 
        # Actually user wants to see "where they were".
        
        m.home_position = engine.get_team_position(m.home_team_id, m.league, m.season, prev_day)
        m.away_position = engine.get_team_position(m.away_team_id, m.league, m.season, prev_day)
        
        result.append(m)
        
    return result


@router.get("/filters/options")
async def get_filter_options(
    league: str | None = None,
    season: str | None = None,
    db: Session = Depends(get_db)
):
    """Get unique leagues, seasons, and teams (optionally filtered)"""
    # 1. Leagues & Seasons (Always fetch distinct from all matches for global context, or filter if needed)
    leagues = db.query(Match.league).distinct().filter(Match.league.isnot(None)).order_by(Match.league).all()
    seasons = db.query(Match.season).distinct().filter(Match.season.isnot(None)).order_by(Match.season.desc()).all()
    
    # 3. Teams with Leagues
    # We want teams that have played matches matching the filters
    # If we want to allow frontend filtering, we should return which leagues the team plays in.
    
    # Efficient query: Get distinct (team_id, league) tuples
    team_league_query = db.query(Match.home_team_id, Match.league).distinct().union(
                        db.query(Match.away_team_id, Match.league).distinct())
    
    team_leagues_map = {}
    for tid, lg in team_league_query.all():
        if tid not in team_leagues_map:
            team_leagues_map[tid] = set()
        if lg:
            team_leagues_map[tid].add(lg)
            
    # Now get Team Objects
    teams_query = db.query(Team).distinct().order_by(Team.name)
    if league:
        # If backend filtering is requested via param
        # We can just filter here or rely on the Map check
        teams_query = teams_query.join(Match, (Match.home_team_id == Team.id) | (Match.away_team_id == Team.id)).filter(Match.league == league)
        
    teams = teams_query.all()
    
    enriched_teams = []
    for t in teams:
        legs = list(team_leagues_map.get(t.id, []))
        legs.sort()
        enriched_teams.append({
            "id": t.id, 
            "name": t.name,
            "leagues": legs
        })
    
    # 4. Rounds (Jornadas)
    # Fetch distinct rounds derived from the filters
    rounds_query = db.query(Match.round).filter(Match.round.isnot(None))
    if league:
        rounds_query = rounds_query.filter(Match.league == league)
    if season:
        rounds_query = rounds_query.filter(Match.season == season)
        
    # We cast to integer to sort nicely (if possible), or just sort string
    # Safe sort:
    raw_rounds = rounds_query.distinct().all()
    # Filter out non-numeric if any, or just sort natural
    # Let's clean up
    cleaned_rounds = []
    for r in raw_rounds:
        val = r[0]
        if val and val.isdigit():
            cleaned_rounds.append(int(val))
    
    cleaned_rounds.sort()
    
    return {
        "leagues": [l[0] for l in leagues],
        "seasons": [s[0] for s in seasons],
        "teams": enriched_teams,
        "rounds": [str(r) for r in cleaned_rounds]
    }
