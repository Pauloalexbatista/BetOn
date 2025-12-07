import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
import json

def test_fetch_round():
    client = APIFootballClient()
    
    # Fetch fixtures for Liga Portugal (94), Season 2024 (or 2025 if current)
    # We'll try to get just one or two to inspect structure
    print("Fetching fixtures...")
    fixtures = client.get_fixtures(league_id=94, season=2023, next_n=5)
    
    if fixtures:
        print(f"Found {len(fixtures)} fixtures.")
        sample = fixtures[0]
        
        # Print Key Round Info
        league_data = sample.get('league', {})
        round_info = league_data.get('round')
        
        print(f"\n--- Sample Fixture ---")
        print(f"Teams: {sample['teams']['home']['name']} vs {sample['teams']['away']['name']}")
        print(f"Date: {sample['fixture']['date']}")
        print(f"Round Raw: '{round_info}'")
        
        print("\n--- Full League Object ---")
        print(json.dumps(league_data, indent=2))
    else:
        print("No fixtures found.")

if __name__ == "__main__":
    test_fetch_round()
