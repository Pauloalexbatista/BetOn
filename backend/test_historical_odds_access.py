import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.api_football import APIFootballClient

def test_single_match_odds():
    client = APIFootballClient()
    
    # 1. Get one finished fixture
    print("Fetching one finished fixture...")
    fixtures = client.get_fixtures(league_id=94, season=2023)
    
    if not fixtures:
        print("No fixtures found.")
        return
        
    # Find a finished match
    finished_fixture = next((f for f in fixtures if f["fixture"]["status"]["short"] == "FT"), None)
    
    if not finished_fixture:
        print("No finished fixture found.")
        return
        
    f_id = finished_fixture["fixture"]["id"]
    home = finished_fixture["teams"]["home"]["name"]
    away = finished_fixture["teams"]["away"]["name"]
    date = finished_fixture["fixture"]["date"]
    
    print(f"Testing odds for: {home} vs {away} (ID: {f_id}, Date: {date})")
    
    # 2. Get Odds
    resp = client.get_odds(fixture_id=f_id)
    
    print("Response:")
    print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    test_single_match_odds()
