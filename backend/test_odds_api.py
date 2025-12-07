import asyncio
import os
# Env loaded by config.py via pydantic-settings

from collectors.the_odds_api import TheOddsAPIClient

async def main():
    print("--- Testing The Odds API ---")
    
    # 1. Init
    client = TheOddsAPIClient()
    if not client.api_key:
        print("ERROR: API Key not found in settings!")
        return

    print(f"API Key loaded. Prefix: {client.api_key[:4]}...")

    # 2. Get Sports (to check connection)
    print("\nFetching available sports...")
    sports = await client.get_sports()
    if isinstance(sports, list):
        print(f"Success! Found {len(sports)} sports.")
        # Print a few examples
        for s in sports[:3]:
            print(f" - {s['key']} ({s['title']})")
    else:
        print(f"Error fetching sports: {sports}")

    # 3. Get Odds for Portuguese League
    print("\nFetching odds for 'soccer_portugal_primeira_liga'...")
    # Using generic 'soccer_portugal_primeira_liga' as default in client
    odds = await client.get_upcoming_odds(sport="soccer_portugal_primeira_liga")
    
    if isinstance(odds, list):
        print(f"Success! Found {len(odds)} matches with odds.")
        if len(odds) > 0:
            match = odds[0]
            print(f"\nSample Match: {match.get('home_team')} vs {match.get('away_team')}")
            print("Bookmakers:", [b['title'] for b in match.get('bookmakers', [])])
    else:
        print(f"Error fetching odds: {odds}")

if __name__ == "__main__":
    asyncio.run(main())
