
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from scripts.update_results import update_all
from database.database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/update")
async def trigger_update(background_tasks: BackgroundTasks):
    """
    Trigger a full system update (Results + Schedule) in the background.
    """
    background_tasks.add_task(update_all)
    return {"message": "Update started in background. Check logs for progress."}

@router.get("/status")
async def get_system_status():
    """
    Get simple system status (Placeholder for now)
    """
    return {"status": "online", "version": "0.1.0"}


@router.get("/api-status")
async def get_api_status() -> Dict[str, Any]:
    """
    Get current API status, quotas, and usage statistics.
    Returns information about API-Football and The Odds API.
    """
    from collectors.api_football import APIFootballClient
    from config import get_settings
    
    settings = get_settings()
    
    result = {
        "api_football": {
            "configured": False,
            "status": "not_configured",
            "quota": None,
            "usage": None
        },
        "the_odds_api": {
            "configured": False,
            "status": "not_configured",
            "quota": None,
            "usage": None
        }
    }
    
    # Check API-Football
    api_football_configured = (
        settings.api_football_key and 
        settings.api_football_key != "" and 
        settings.api_football_key != "your_api_football_key"
    )
    
    if api_football_configured:
        result["api_football"]["configured"] = True
        try:
            client = APIFootballClient()
            status_response = client.get_status()
            
            if "response" in status_response and status_response["response"]:
                api_data = status_response["response"]
                
                # Extract quota information
                requests = api_data.get("requests", {})
                result["api_football"]["status"] = "active"
                result["api_football"]["quota"] = {
                    "limit_day": requests.get("limit_day", "Unknown"),
                    "current": requests.get("current", 0),
                    "remaining": requests.get("limit_day", 0) - requests.get("current", 0) if requests.get("limit_day") else None
                }
                result["api_football"]["usage"] = {
                    "today": requests.get("current", 0),
                    "percentage": round((requests.get("current", 0) / requests.get("limit_day", 1)) * 100, 1) if requests.get("limit_day") else 0
                }
                
                # Account info
                if "account" in api_data:
                    result["api_football"]["account"] = {
                        "firstname": api_data["account"].get("firstname"),
                        "lastname": api_data["account"].get("lastname"),
                        "email": api_data["account"].get("email")
                    }
                
                # Subscription info
                if "subscription" in api_data:
                    result["api_football"]["subscription"] = {
                        "plan": api_data["subscription"].get("plan"),
                        "end": api_data["subscription"].get("end"),
                        "active": api_data["subscription"].get("active", False)
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching API-Football status: {e}")
            result["api_football"]["status"] = "error"
            result["api_football"]["error"] = str(e)
    
    # Check The Odds API
    odds_api_configured = (
        settings.the_odds_api_key and 
        settings.the_odds_api_key != "" and 
        settings.the_odds_api_key != "your_theodds_api_key"
    )
    
    if odds_api_configured:
        result["the_odds_api"]["configured"] = True
        result["the_odds_api"]["status"] = "configured"
        result["the_odds_api"]["info"] = {
            "note": "The Odds API does not provide a status endpoint. Check usage at: https://the-odds-api.com/account/",
            "free_tier_limit": "500 requests/month"
        }
    
    return result


@router.get("/database-status")
async def get_database_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get database status and record counts.
    Helps identify what data is missing.
    """
    from database.models import Team, Match, Odds, Strategy, Bet
    from sqlalchemy import func
    
    try:
        # Count records
        teams_count = db.query(Team).count()
        matches_total = db.query(Match).count()
        matches_finished = db.query(Match).filter(Match.status == "finished").count()
        matches_scheduled = db.query(Match).filter(Match.status == "scheduled").count()
        odds_count = db.query(Odds).count()
        strategies_count = db.query(Strategy).count()
        bets_count = db.query(Bet).count()
        
        # Get league/season breakdown
        league_stats = db.query(
            Match.league,
            Match.season,
            func.count(Match.id).label('count')
        ).group_by(Match.league, Match.season).all()
        
        leagues_data = [
            {"league": stat[0], "season": stat[1], "matches": stat[2]}
            for stat in league_stats
        ]
        
        # Determine status
        has_data = matches_total > 0
        status = "healthy" if has_data else "empty"
        
        warnings = []
        if matches_total == 0:
            warnings.append("No matches in database. Run data collectors to populate.")
        if odds_count == 0 and matches_total > 0:
            warnings.append("No odds data. Consider running odds collectors.")
        if matches_scheduled == 0:
            warnings.append("No upcoming matches. Update schedule data.")
        
        return {
            "status": status,
            "counts": {
                "teams": teams_count,
                "matches_total": matches_total,
                "matches_finished": matches_finished,
                "matches_scheduled": matches_scheduled,
                "odds": odds_count,
                "strategies": strategies_count,
                "bets": bets_count
            },
            "leagues": leagues_data,
            "warnings": warnings,
            "suggestions": [
                "Run: python collectors/football_data_co_uk.py" if matches_total == 0 else None,
                "Run: python collectors/schedule_collector.py" if matches_scheduled == 0 else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
