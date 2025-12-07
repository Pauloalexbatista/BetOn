import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.the_odds_api import TheOddsAPIClient

async def test_odds_structure():
    client = TheOddsAPIClient()
    
    print("Fetching odds from The Odds API...")
    # Using 'soccer_portugal_primeira_liga' as default test
    data = await client.get_upcoming_odds(sport="soccer_portugal_primeira_liga", regions="eu", markets="h2h")
    
    if isinstance(data, list) and len(data) > 0:
        print(f"Received {len(data)} events.")
        sample = data[0]
        
        print("\n--- Sample Event Structure ---")
        # Print basic info
        print(f"ID: {sample.get('id')}")
        print(f"Sport: {sample.get('sport_key')}")
        print(f"Time: {sample.get('commence_time')}")
        print(f"Home: {sample.get('home_team')}")
        print(f"Away: {sample.get('away_team')}")
        
        # Check for any "round" or "week" keys in the top level
        print("\n--- Potential Round Keys ---")
        for key in sample.keys():
            if "round" in key.lower() or "week" in key.lower() or "group" in key.lower():
                print(f"{key}: {sample[key]}")
                
        print("\n--- Full Object Dump (First Item) ---")
        print(json.dumps(sample, indent=2))
        
    else:
        print("No events found or error.")
        print(data)

if __name__ == "__main__":
    asyncio.run(test_odds_structure())
