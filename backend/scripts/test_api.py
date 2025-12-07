import asyncio
import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
from config import get_settings

def test_api_connection():
    print("\n⚽ Testing API-Football Connection...")
    print("====================================")
    
    settings = get_settings()
    if not settings.api_football_key or "your_" in settings.api_football_key:
        print("❌ ERROR: API Key not set in .env file!")
        print("Please edit .env and add your API_FOOTBALL_KEY")
        return

    client = APIFootballClient()
    
    # 1. Check Status
    print("\n1. Checking Account Status...")
    status = client.get_status()
    if not status or status.get("errors"):
        print(f"❌ Failed: {status.get('errors')}")
        return
    
    account = status.get("response", {}).get("account", {})
    requests = status.get("response", {}).get("requests", {})
    print(f"✅ Connection Successful!")
    print(f"   Name: {account.get('firstname')} {account.get('lastname')}")
    print(f"   Email: {account.get('email')}")
    print(f"   Requests Today: {requests.get('current')}/{requests.get('limit_day')}")

    # 2. Get Portugal Leagues
    print("\n2. Fetching Portuguese Leagues...")
    leagues = client.get_leagues(country="Portugal")
    liga_portugal = next((l for l in leagues if l["league"]["name"] == "Primeira Liga"), None)
    
    if liga_portugal:
        league_id = liga_portugal["league"]["id"]
        print(f"✅ Found Primeira Liga (ID: {league_id})")
        
        # 3. Check Available Seasons
        print("\n3. Checking Coverage for Primeiral Liga...")
        seasons = liga_portugal["seasons"]
        available_years = []
        current_season = None
        
        for s in seasons:
            year = s["year"]
            available_years.append(year)
            if s["current"]:
                current_season = year
                print(f"   ► Season {year} (Current): Events={s['coverage']['fixtures']['events']}, Odds={s['coverage']['odds']}")
            else:
                print(f"   Season {year}: Available")
                
        print(f"\n   Available Years: {available_years}")
        
        target_season = 2023
        print(f"\n4. Fetching Fixtures for Season {target_season} (Historical Data)...")
        
        # for historical data, 'next' might not work well if season is over. 
        # let's get last 5 matches instead to be safe, or just list some fixtures.
        fixtures = client.get_fixtures(league_id=league_id, season=target_season, date='2023-11-12') # Testing specific date in 2023 season
        
        if not fixtures:
             # Try getting first round if specific date fails
             fixtures = client.get_fixtures(league_id=league_id, season=target_season)
             if fixtures:
                 fixtures = fixtures[:5] 
        
        if fixtures:
            for f in fixtures:
                home = f["teams"]["home"]["name"]
                away = f["teams"]["away"]["name"]
                date = f["fixture"]["date"]
                score = f"{f['goals']['home']}-{f['goals']['away']}"
                print(f"   📅 {date[:10]}: {home} {score} {away}")
        else:
            print(f"   ⚠️ No fixtures found for {target_season}")
            
    else:
        print("⚠️ Primeira Liga not found in response")

    print("\n====================================")
    print("🎉 Test Complete!")

if __name__ == "__main__":
    test_api_connection()
