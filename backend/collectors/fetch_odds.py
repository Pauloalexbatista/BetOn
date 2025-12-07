import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Team, Match, Odds
from collectors.api_football import APIFootballClient
import json

def fetch_historical_odds(league_id: int, season: int):
    client = APIFootballClient()
    db = SessionLocal()
    
    current_page = 1
    total_pages = 1
    
    print(f"--- Fetching Historical Odds (League: {league_id}, Season: {season}) ---")
    
    while current_page <= total_pages:
        print(f"Processing Page {current_page}/{total_pages}...")
        
        data = client.get_odds(league_id=league_id, season=season, page=current_page)
        
        if "errors" in data and data["errors"]:
            print(f"API Error: {data['errors']}")
            break
            
        # Update Pagination Info
        paging = data.get("paging", {})
        total_pages = paging.get("total", 1)
        
        odds_list = data.get("response", [])
        if not odds_list:
            print("No odds found on this page.")
            break
            
        # Process Each Odds Record
        for item in odds_list:
            fixture_data = item["fixture"] # {id, date, ...}
            teams_data = item["teams"] # {home: {id, name}, away: {id, name}}
            bookmakers = item["bookmakers"]
            
            # We need to find the Match in our DB.
            # We don't have fixture_id, so we match by HOME TEAM ID (api_id) and AWAY TEAM ID (api_id).
            
            home_api_id = str(teams_data["home"]["id"])
            away_api_id = str(teams_data["away"]["id"])
            
            # Find DB Teams
            home_team = db.query(Team).filter(Team.api_id == home_api_id).first()
            away_team = db.query(Team).filter(Team.api_id == away_api_id).first()
            
            if not home_team or not away_team:
                # print(f"Skipping match (Teams not found): {teams_data['home']['name']} vs {teams_data['away']['name']}")
                continue
                
            # Find Match
            # Assuming match_date is close enough or simply by matching league/season/teams (which are unique per season usually)
            # Actually, just Team inputs are usually enough for same season.
            
            match = db.query(Match).filter(
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
                Match.season == str(season)
            ).first()
            
            if not match:
                # print(f"Match not found in DB: {home_team.name} vs {away_team.name}")
                continue
                
            # Process Bookmakers (Focus on Bet365 or generic)
            # We will store ALL bookmakers as JSON list, or simplify.
            # Model `Odds` expects: id, match_id, bookmaker, odds_data (JSON)
            
            # Clear existing odds for this match to avoid duplicates (optional, or check)
            # db.query(Odds).filter(Odds.match_id == match.id).delete()
            
            count_new = 0
            for bookie in bookmakers:
                bookie_name = bookie["name"]
                
                # Extract '1x2' market usually id=1
                # Format: values: [{value: "Home", odd: "1.5"}, ...]
                
                market_1x2 = next((m for m in bookie["bets"] if m["id"] == 1), None)
                if not market_1x2: continue
                
                # Convert to clean JSON: {home: 1.5, draw: 3.2, away: 5.0}
                clean_odds = {}
                for selection in market_1x2["values"]:
                    val = selection["value"] # "Home", "Draw", "Away"
                    odd = float(selection["odd"])
                    clean_odds[val.lower()] = odd
                    
                # Create Odds Record
                # Check if exists first
                existing_odd = db.query(Odds).filter(
                    Odds.match_id == match.id,
                    Odds.bookmaker == bookie_name
                ).first()
                
                if existing_odd:
                    existing_odd.odds_data = clean_odds
                    existing_odd.timestamp = datetime.now()
                else:
                    new_odd = Odds(
                        match_id=match.id,
                        bookmaker=bookie_name,
                        odds_data=clean_odds,
                        timestamp=datetime.now()
                    )
                    db.add(new_odd)
                count_new += 1
                
            # print(f"Saved {count_new} odds records for {home_team.name} vs {away_team.name}")
        
        db.commit()
        current_page += 1
        time.sleep(1) # Rate limit respect
        
    print("Done!")
    db.close()

from datetime import datetime

if __name__ == "__main__":
    # Portugal, 2023
    fetch_historical_odds(league_id=94, season=2023)
