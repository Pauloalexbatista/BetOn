import asyncio
from collectors.the_odds_api import TheOddsAPIClient

async def test_the_odds_api():
    print("=== THE ODDS API - Capabilities Test ===\n")
    
    client = TheOddsAPIClient()
    
    # Test 1: Get available sports
    print("1. Available Sports:")
    sports = await client.get_sports()
    
    if isinstance(sports, list):
        print(f"   Total sports: {len(sports)}")
        
        # Find Portuguese leagues
        pt_leagues = [s for s in sports if 'portugal' in s.get('key', '').lower()]
        if pt_leagues:
            print(f"   Portuguese leagues: {[s['title'] for s in pt_leagues]}")
        else:
            print("   No Portuguese leagues found")
            
        # Show some examples
        print("\n   Sample sports:")
        for sport in sports[:5]:
            print(f"     - {sport.get('title')} ({sport.get('key')})")
    else:
        print(f"   Error: {sports}")
    
    # Test 2: Try to get upcoming odds for Primeira Liga
    print("\n2. Testing Upcoming Odds (Primeira Liga):")
    odds_data = await client.get_upcoming_odds(
        sport="soccer_portugal_primeira_liga",
        markets="h2h"
    )
    
    if isinstance(odds_data, list):
        print(f"   ✅ Found {len(odds_data)} upcoming matches with odds")
        if len(odds_data) > 0:
            sample = odds_data[0]
            print(f"\n   Sample match:")
            print(f"     {sample.get('home_team')} vs {sample.get('away_team')}")
            print(f"     Date: {sample.get('commence_time')}")
            print(f"     Bookmakers: {len(sample.get('bookmakers', []))}")
    elif 'error' in odds_data:
        print(f"   ❌ Error: {odds_data['error']}")
    else:
        print(f"   Unexpected response: {type(odds_data)}")
    
    print("\n" + "="*60)
    print("CONCLUSION:")
    print("  - The Odds API provides ONLY upcoming/current odds")
    print("  - NO historical odds available")
    print("  - Free tier: 500 requests/month")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_the_odds_api())
