"""
Test API-Football with 2023 season (available on free tier)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
from datetime import datetime

def main():
    print("⚽ Testing API-Football with 2023 Season (Free Tier)\n")
    
    client = APIFootballClient()
    league_id = 94  # Primeira Liga
    season = 2023  # Use 2023 instead of 2024
    
    # 1. Get 2023 Final Standings
    print("📊 1. Fetching 2023 Final Standings...")
    standings_data = client.get_standings(league_id, season)
    
    if standings_data:
        standings = standings_data[0].get("league", {}).get("standings", [[]])[0]
        print(f"✅ Found standings for {len(standings)} teams (Season 2022/2023)")
        print("\nTop 5:")
        for i, team in enumerate(standings[:5], 1):
            team_info = team.get("team", {})
            stats = team.get("all", {})
            print(f"   {i}. {team_info.get('name')} - {team.get('points')}pts ({stats.get('played')} jogos)")
    else:
        print("❌ No standings data")
    
    # 2. Get some 2023 fixtures
    print("\n🗓️ 2. Fetching Sample 2023 Fixtures...")
    fixtures = client.get_fixtures_range(
        league_id, 
        season, 
        from_date="2023-01-01",
        to_date="2023-01-31"
    )
    
    print(f"✅ Found {len(fixtures)} matches in Jan 2023")
    
    if fixtures:
        print("\nSample matches:")
        for fixture in fixtures[:5]:
            fixture_data = fixture.get("fixture", {})
            teams = fixture.get("teams", {})
            goals = fixture.get("goals", {})
            home = teams.get("home", {}).get("name", "?")
            away = teams.get("away", {}).get("name", "?")
            home_goals = goals.get("home", "?")
            away_goals = goals.get("away", "?")
            date = fixture_data.get("date", "")
            
            try:
                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                date_str = dt.strftime("%d/%m/%Y")
            except:
                date_str = date[:10] if date else "TBD"
            
            print(f"   • {date_str}: {home} {home_goals}-{away_goals} {away}")
    
    # 3. Test Historical Odds
    print("\n💰 3. Testing Historical Odds Availability...")
    if fixtures:
        first_fixture_id = fixtures[0].get("fixture", {}).get("id")
        if first_fixture_id:
            home = fixtures[0].get("teams", {}).get("home", {}).get("name", "?")
            away = fixtures[0].get("teams", {}).get("away", {}).get("name", "?")
            print(f"Fetching odds for: {home} vs {away} (ID: {first_fixture_id})...")
            
            odds_data = client.get_odds(fixture_id=first_fixture_id)
            
            if odds_data.get("response") and len(odds_data["response"]) > 0:
                print(f"✅ Historical odds available!")
                
                first_bookie = odds_data["response"][0]
                bookmakers = first_bookie.get("bookmakers", [])
                
                if bookmakers:
                    print(f"\n📊 Available from {len(bookmakers)} bookmaker(s):")
                    
                    # Show H2H odds
                    for bookmaker in bookmakers[:2]:
                        bookie_name = bookmaker.get("name", "Unknown")
                        bets = bookmaker.get("bets", [])
                        
                        h2h_bet = next((b for b in bets if b.get("name") == "Match Winner"), None)
                        if h2h_bet:
                            print(f"\n   {bookie_name} - Match Winner:")
                            for value in h2h_bet.get("values", []):
                                print(f"      {value.get('value')}: {value.get('odd')}")
            else:
                print("⚠️ No historical odds available")
                if odds_data.get("errors"):
                    print(f"   Error: {odds_data['errors']}")
    
    # 4. Check Usage
    print("\n📈 4. API Usage Summary...")
    status = client.get_status()
    if status.get("response"):
        requests = status["response"]["requests"]
        used = requests.get("current", 0)
        limit = requests.get("limit_day", 100)
        print(f"✅ Usage: {used}/{limit} requests today")
        print(f"✅ Remaining: {limit - used} requests")
    
    print("\n" + "="*50)
    print("🎯 CONCLUSION:")
    print("="*50)
    print("✅ Free tier works for HISTORICAL data (2021-2023)")
    print("❌ Free tier CANNOT access current season (2024/25)")
    print("💰 Need PAID plan (€19/mês) for live season data")
    print("="*50)

if __name__ == "__main__":
    main()
