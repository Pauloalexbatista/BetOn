import sys
import os
import logging
import time
from datetime import datetime, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Match, Team
from collectors.api_football import APIFootballClient
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapping from our DB League Names to API-Football League IDs
LEAGUE_MAPPING = {
    "Primeira Liga": 94,
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61
}

# Team Name Mappings (Manual Overrides)
TEAM_MAPPINGS = {
    "Sp Lisbon": "Sporting CP",
    "Man United": "Man United",
    "Man City": "Man City",
    "Nott'm Forest": "Nott'm Forest",
}

def backfill_rounds():
    db = SessionLocal()
    client = APIFootballClient()
    
    try:
        # 1. Identify what we have in DB
        series = db.query(Match.league, Match.season).distinct().all()
        logger.info(f"Found {len(series)} League/Season combinations in DB.")
        
        for league_name, season_str in series:
            if not season_str or "/" not in season_str:
                continue
                
            start_year = int(season_str.split("/")[0])
            league_id = LEAGUE_MAPPING.get(league_name)
            
            if not league_id:
                logger.warning(f"Skipping {league_name}: No mapped ID.")
                continue

            # Skip Portugal as it is already done
            if league_name == "Primeira Liga":
                logger.info("Skipping Primeira Liga (Already Backfilled)")
                continue

            logger.info(f"Processing {league_name} ({season_str}) -> API ID {league_id}, Year {start_year}")
            
            # 2. Fetch ALL fixtures for this league/season from API
            try:
                fixtures = client.get_fixtures(league_id=league_id, season=start_year)
                logger.info(f"  Fetched {len(fixtures)} fixtures from API.")
                
                updates_count = 0
                
                # 3. Match and Update
                for f in fixtures:
                    fixture_date_str = f['fixture']['date']
                    api_dt = datetime.fromisoformat(fixture_date_str.replace("Z", "+00:00"))
                    api_date = api_dt.date()
                    
                    # Extract Round
                    raw_round = f['league'].get('round')
                    parsed_round = parse_round(raw_round)
                    
                    if not parsed_round:
                        continue
                        
                    # Teams
                    home_name_api = f['teams']['home']['name']
                    away_name_api = f['teams']['away']['name']
                    
                    # Find Match in DB
                    candidates = db.query(Match).filter(
                        Match.league == league_name,
                        Match.season == season_str,
                        func.date(Match.match_date) == api_date
                    ).all()
                    
                    matched_db_match = None
                    for candidate in candidates:
                        c_home = db.query(Team).get(candidate.home_team_id)
                        c_away = db.query(Team).get(candidate.away_team_id)
                        
                        if is_match(home_name_api, c_home.name) and is_match(away_name_api, c_away.name):
                            matched_db_match = candidate
                            break
                    
                    if matched_db_match:
                        if matched_db_match.round != parsed_round:
                            matched_db_match.round = parsed_round
                            updates_count += 1
                            
                db.commit()
                logger.info(f"  Updated {updates_count} matches with round info.")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {league_name} {season_str}: {e}")
                
    except Exception as e:
        logger.error(f"Fatal script error: {e}")
    finally:
        db.close()

def parse_round(round_str):
    if not round_str: return None
    import re
    match = re.search(r'(\d+)$', round_str)
    if match:
        return match.group(1)
    return round_str

def is_match(api_name, db_name):
    if api_name == db_name: return True
    if TEAM_MAPPINGS.get(api_name) == db_name: return True
    if api_name in db_name or db_name in api_name: return True
    return False

if __name__ == "__main__":
    print("WARNING: This script will consume API Quota (All Leagues except Portugal).")
    backfill_rounds()
