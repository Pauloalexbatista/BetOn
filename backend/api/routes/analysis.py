from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional, Dict

from database.database import get_db
from database.models import Match

router = APIRouter()

@router.get("/league-pulse")
def get_league_pulse(
    league: Optional[str] = None,
    season: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics by League and/or Season.
    Flexible filters allow viewing all data or filtering by league/season.
    """
    
    # Handle empty strings as None
    if league == "": league = None
    if season == "": season = None
    
    # 1. Base Query
    query = db.query(Match).filter(Match.status == "finished", Match.home_score.isnot(None))
    
    if league:
        query = query.filter(Match.league == league)
    if season:
        query = query.filter(Match.season == season)
        
    matches = query.all()
    
    # 2. Grouping
    # Key: (league, season) -> list of matches
    grouped = {}
    
    for m in matches:
        key = (m.league, m.season)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(m)
        
    results = []
    
    # 3. Calculate Stats for each group
    for (lg, sea), group_matches in grouped.items():
        total_matches = len(group_matches)
        
        total_goals = 0
        btts_count = 0
        over_1_5_count = 0
        over_2_5_count = 0
        home_wins = 0
        draws = 0
        away_wins = 0
        
        for m in group_matches:
            h = m.home_score
            a = m.away_score
            total = h + a
            total_goals += total
            
            if h > 0 and a > 0: btts_count += 1
            if total > 1.5: over_1_5_count += 1
            if total > 2.5: over_2_5_count += 1
            
            if h > a: home_wins += 1
            elif a > h: away_wins += 1
            else: draws += 1
            
        stats = {
            "league": lg,
            "season": sea,
            "total_matches": total_matches,
            "avg_goals": round(total_goals / total_matches, 2),
            "btts_pct": round((btts_count / total_matches) * 100, 1),
            "over_1_5_pct": round((over_1_5_count / total_matches) * 100, 1),
            "over_2_5_pct": round((over_2_5_count / total_matches) * 100, 1),
            "home_win_pct": round((home_wins / total_matches) * 100, 1),
            "draw_pct": round((draws / total_matches) * 100, 1),
            "away_win_pct": round((away_wins / total_matches) * 100, 1)
        }
        results.append(stats)
        
    # Sort results effectively (by League then Season desc)
    results.sort(key=lambda x: (x['league'], x['season']), reverse=True)

    return results

@router.get("/team-pulse")
def get_team_pulse(
    league: Optional[str] = None,
    season: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics PER TEAM.
    Can filter by league and/or season, or show all teams.
    """
    
    # Handle empty strings as None
    if league == "": league = None
    if season == "": season = None
    
    # 1. Query
    query = db.query(Match).filter(
        Match.status == "finished",
        Match.home_score.isnot(None)
    )
    
    if league:
        query = query.filter(Match.league == league)
    if season:
        query = query.filter(Match.season == season)
        
    matches = query.all()
    
    # 2. Accumulate
    # Struct: team_name -> { h_p, h_w, h_d, h_l, ... }
    # We use team name as key for simplicity (assuming unique within league/season)
    # Ideally should use ID, but frontend needs Name.
    # We can fetch names from relationship if query included joinedload.
    # For now, simplistic loop is fine for <500 matches.
    
    stats = {}
    
    def get_init():
        return {
            "matches": 0,
            "goals_for": 0,
            "goals_against": 0,
            
            # Counts for percentages
            "btts": 0,
            "over_1_5": 0,
            "over_2_5": 0,
            
            # Home Specific
            "home_matches": 0,
            "home_wins": 0,
            "home_draws": 0,
            "home_loss": 0,
            
             # Away Specific (for completeness, though League Pulse ui focuses on Home Win % col)
            "away_matches": 0,
            "away_wins": 0,
            "away_draws": 0,
            "away_loss": 0,
        }
    
    for m in matches:
        if not m.home_team or not m.away_team:
            continue # Skip corrupt
            
        h_name = m.home_team.name
        a_name = m.away_team.name
        
        if h_name not in stats: stats[h_name] = get_init()
        if a_name not in stats: stats[a_name] = get_init()
        
        h_score = m.home_score
        a_score = m.away_score
        total = h_score + a_score
        
        # Shared flags
        is_btts = (h_score > 0 and a_score > 0)
        is_o15 = (total > 1.5)
        is_o25 = (total > 2.5)
        
        # --- Update Home Team ---
        s = stats[h_name]
        s["matches"] += 1
        s["goals_for"] += h_score
        s["goals_against"] += a_score
        s["home_matches"] += 1
        
        if is_btts: s["btts"] += 1
        if is_o15: s["over_1_5"] += 1
        if is_o25: s["over_2_5"] += 1
        
        if h_score > a_score: s["home_wins"] += 1
        elif h_score == a_score: s["home_draws"] += 1
        else: s["home_loss"] += 1
            
        # --- Update Away Team ---
        s = stats[a_name]
        s["matches"] += 1
        s["goals_for"] += a_score
        s["goals_against"] += h_score
        s["away_matches"] += 1
        
        if is_btts: s["btts"] += 1
        if is_o15: s["over_1_5"] += 1
        if is_o25: s["over_2_5"] += 1
        
        if a_score > h_score: s["away_wins"] += 1
        elif a_score == h_score: s["away_draws"] += 1
        else: s["away_loss"] += 1

    # 3. Format
    results = []
    for name, s in stats.items():
        tm = s["matches"]
        hm = s["home_matches"]
        am = s["away_matches"]
        
        if tm == 0: continue
        
        # Matches existing LeagueStat interface columns
        res = {
            "team": name,
            "league": league if league else "Multiple",
            "season": season if season else "Multiple",
            "total_matches": tm,
            "avg_goals": round((s["goals_for"] + s["goals_against"]) / tm, 2),
            
            "btts_pct": round((s["btts"] / tm) * 100, 1),
            "over_1_5_pct": round((s["over_1_5"] / tm) * 100, 1),
            "over_2_5_pct": round((s["over_2_5"] / tm) * 100, 1),
            
            # Home Win % (Specific to Team's home games)
            "home_win_pct": round((s["home_wins"] / hm) * 100, 1) if hm > 0 else 0,
            
            "draw_pct": round(((s["home_draws"] + s["away_draws"]) / tm) * 100, 1), # Overall Draw %
            
            # Away Win % (Specific to Team's away games)
            "away_win_pct": round((s["away_wins"] / am) * 100, 1) if am > 0 else 0,
        }
        
        results.append(res)
        
    # Sort alphabetically by default
    results.sort(key=lambda x: x['team'])
    return results
