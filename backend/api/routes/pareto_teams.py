from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional, Dict

from database.database import get_db
from database.models import Match, Team

router = APIRouter()


@router.get("/pareto-teams")
def get_pareto_teams(
    season: Optional[str] = None,
    market: str = Query(default="win_rate"),
    min_matches: int = Query(default=5, ge=1),
    db: Session = Depends(get_db)
):
    """
    Get team rankings filtered by season and market
    
    Args:
        season: Season filter (e.g., '2025/2026') or None for all seasons
        market: Market type ('win_rate', 'over_2.5', 'btts_yes', 'home_win')
        min_matches: Minimum matches to include team
    """
    # Build base query
    query = db.query(Match).filter(Match.status == 'finished')
    
    if season:
        query = query.filter(Match.season == season)
    
    matches = query.all()
    
    if not matches:
        return {
            "teams": [],
            "total_matches": 0,
            "season": season or "All",
            "market": market
        }
    
    # Calculate team stats
    team_stats = {}
    
    for match in matches:
        home_id = match.home_team_id
        away_id = match.away_team_id
        
        # Initialize teams
        for team_id in [home_id, away_id]:
            if team_id not in team_stats:
                team_stats[team_id] = {
                    'matches': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'over_25': 0,
                    'btts': 0,
                    'home_wins': 0,
                    'home_matches': 0
                }
        
        total_goals = match.home_score + match.away_score
        
        # Home team stats
        team_stats[home_id]['matches'] += 1
        team_stats[home_id]['home_matches'] += 1
        
        if total_goals > 2.5:
            team_stats[home_id]['over_25'] += 1
        
        if match.home_score > 0 and match.away_score > 0:
            team_stats[home_id]['btts'] += 1
        
        if match.home_score > match.away_score:
            team_stats[home_id]['wins'] += 1
            team_stats[home_id]['home_wins'] += 1
        elif match.home_score == match.away_score:
            team_stats[home_id]['draws'] += 1
        else:
            team_stats[home_id]['losses'] += 1
        
        # Away team stats
        team_stats[away_id]['matches'] += 1
        
        if total_goals > 2.5:
            team_stats[away_id]['over_25'] += 1
        
        if match.home_score > 0 and match.away_score > 0:
            team_stats[away_id]['btts'] += 1
        
        if match.away_score > match.home_score:
            team_stats[away_id]['wins'] += 1
        elif match.home_score == match.away_score:
            team_stats[away_id]['draws'] += 1
        else:
            team_stats[away_id]['losses'] += 1
    
    # Filter by minimum matches and calculate percentages
    teams_list = []
    
    for team_id, stats in team_stats.items():
        if stats['matches'] < min_matches:
            continue
        
        # Get team name
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            continue
        
        win_rate = round((stats['wins'] / stats['matches']) * 100, 2)
        over_25_rate = round((stats['over_25'] / stats['matches']) * 100, 2)
        btts_rate = round((stats['btts'] / stats['matches']) * 100, 2)
        home_win_rate = round((stats['home_wins'] / stats['home_matches']) * 100, 2) if stats['home_matches'] > 0 else 0
        
        points = (stats['wins'] * 3) + stats['draws']
        points_pct = round((points / (stats['matches'] * 3)) * 100, 2)
        
        team_data = {
            'id': team_id,
            'team_id': team_id,
            'name': team.name,
            'league': team.league,
            'leagues': [team.league] if team.league else [],
            'country': team.country,
            'total_matches': stats['matches'],
            'wins': stats['wins'],
            'draws': stats['draws'],
            'losses': stats['losses'],
            'win_rate': win_rate,
            'over_25_rate': over_25_rate,
            'btts_rate': btts_rate,
            'home_win_rate': home_win_rate,
            'points': points,
            'points_percentage': points_pct
        }
        
        teams_list.append(team_data)
    
    # Sort by selected market
    if market == 'over_2.5':
        teams_list.sort(key=lambda x: x['over_25_rate'], reverse=True)
    elif market == 'btts_yes':
        teams_list.sort(key=lambda x: x['btts_rate'], reverse=True)
    elif market == 'home_win':
        teams_list.sort(key=lambda x: x['home_win_rate'], reverse=True)
    else:  # win_rate (default)
        teams_list.sort(key=lambda x: x['win_rate'], reverse=True)
    
    # Calculate top 20%
    top_20_count = max(1, int(len(teams_list) * 0.2))
    
    return {
        "teams": teams_list,
        "top_20_percent": teams_list[:top_20_count],
        "top_20_count": top_20_count,
        "total_teams": len(teams_list),
        "total_matches": len(matches),
        "season": season or "All Seasons",
        "market": market
    }
