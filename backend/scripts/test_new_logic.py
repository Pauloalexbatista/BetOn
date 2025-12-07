import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 0. Cleanup (Optional)
    # Check if exists and delete
    existing = requests.get(f"{BASE_URL}/strategies/")
    for s in existing.json():
        if s['name'] == "Test Over 2.5 Strategy":
            requests.delete(f"{BASE_URL}/strategies/{s['id']}")
            print(f"Deleted old strategy {s['id']}")

    # 1. Create Strategy (Over 2.5 Goals)
    print("Creating Strategy...")
    payload = {
        "name": "Test Over 2.5 Strategy",
        "description": "Testing the new target_outcome field",
        "target_outcome": "over_2.5",
        "is_active": True,
        "conditions": [
            {
                "entity": "match", # Dummy condition for now to ensure we get matches
                "context": "overall",
                "metric": "goals_scored", # Just pass valid metrics
                "operator": ">",
                "value": 0, # Trigger on everything
                "last_n_games": 3
            }
        ]
    }
    
    try:
        res = requests.post(f"{BASE_URL}/strategies/", json=payload)
        if res.status_code == 200:
            strategy = res.json()
            print(f"Strategy Created: ID {strategy['id']} - Target: {strategy['target_outcome']}")
            
            # 2. Run Backtest
            print("Running Backtest...")
            bt_res = requests.post(f"{BASE_URL}/strategies/{strategy['id']}/backtest")
            results = bt_res.json()
            
            print(f"Backtest Results: {len(results)} bets")
            if results:
                print("Sample Results:")
                for r in results[:5]:
                    print(f"{r['date']} - {r['home']} vs {r['away']} | Result: {r['result']}")
        else:
            print(f"Failed to create strategy: {res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_flow()
