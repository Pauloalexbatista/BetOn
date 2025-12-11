"""
Fetch comprehensive Primeira Liga data from API-Football
Tests: Fixtures, Standings, and Odds availability
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
from datetime import datetime
import json

def main():
    print("⚽ Fetching Primeira Liga Data from API-Football\n")
    
    client = APIFootballClient()
    league_id = 94  # Primeira Liga
    season = 2024  # Season 2024/2025
    
    # 1. Get Current Standings
    print("📊 1. Fetching Current Standings...")
    standings_data = client.get_standings(league_id, season)
    
    if standings_data:
        standings = standings_data[0].get("league", {}).get("standings", [[]])[0]
        print(f"✅ Found standings for {len(standings)} teams")
        print("\nTop 5:")
        for i, team in enumerate(standings[:5], 1):
            team_info = team.get("team", {})
            stats = team.get("all", {})
            print(f"   {i}. {team_info.get('name')} - {team.get('points')}pts ({stats.get('played')} jogos)")
    else:
        print("❌ No standings data")
    
    # 2. Get Next 10 Fixtures
    print("\n🗓️ 2. Fetching Next 10 Fixtures...")
    fixtures = client.get_fixtures(league_id, season, next_n=10)
    
    print(f"✅ Found {len(fixtures)} upcoming matches")
    
    if fixtures:
        print("\nNext matches:")
        for fixture in fixtures[:5]:
            fixture_data = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            home = teams.get("home", {}).get("name", "?")
            away = teams.get("away", {}).get("name", "?")
            date = fixture_data.get("date", "")
            status = fixture_data.get("status", {}).get("short", "")
            
            # Parse date
            try:
                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                date_str = dt.strftime("%d/%m %H:%M")
            except:
                date_str = date[:10] if date else "TBD"
            
            print(f"   • {home} vs {away} - {date_str} ({status})")
            
            # Check if odds are available
            fixture_id = fixture_data.get("id")
            if fixture_id:
                print(f"     Fixture ID: {fixture_id}")
    
    # 3. Test Odds Fetching (for one fixture)
    print("\n💰 3. Testing Odds Availability...")
    if fixtures:
        first_fixture_id = fixtures[0].get("fixture", {}).get("id")
        if first_fixture_id:
            print(f"Fetching odds for fixture {first_fixture_id}...")
            odds_data = client.get_odds(fixture_id=first_fixture_id)
            
            if odds_data.get("response"):
                odds_response = odds_data["response"]
                print(f"✅ Odds available from {len(odds_response)} bookmakers")
                
                # Show first bookmaker's odds
                if odds_response:
                    first_bookie = odds_response[0]
                    bookmaker = first_bookie.get("bookmakers", [{}])[0]
                    bookmaker_name = bookmaker.get("name", "Unknown")
                    bets = bookmaker.get("bets", [])
                    
                    print(f"\nExample odds from {bookmaker_name}:")
                    for bet in bets[:3]:  # Show first 3 markets
                        bet_name = bet.get("name", "?")
                        values = bet.get("values", [])
                        print(f"   • {bet_name}:")
                        for value in values[:3]:  # Show first 3 options
                            print(f"      - {value.get('value')}: {value.get('odd')}")
            else:
                print("⚠️ No odds available for this fixture")
                if odds_data.get("errors"):
                    print(f"   Error: {odds_data['errors']}")
    
    # 4. Check API Usage
    print("\n📈 4. Checking API Usage After Tests...")
    status = client.get_status()
    if status.get("response"):
        requests = status["response"]["requests"]
        used = requests.get("current", 0)
        limit = requests.get("limit_day", 100)
        print(f"✅ Usage: {used}/{limit} requests today")
        print(f"✅ Remaining: {limit - used} requests")
    
    print("\n✅ Data collection test complete!")

if __name__ == "__main__":
    main()
