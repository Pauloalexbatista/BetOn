import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_signals():
    print("Testing Signals Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/signals/today?hours=48")
        if res.status_code == 200:
            data = res.json()
            print(f"Signals Found: {data['count']}")
            for s in data['signals']:
                print(f"Match: {s['home']} vs {s['away']} | Strategy: {s['strategy_name']} | Target: {s['target_outcome']}")
        else:
            print(f"Error: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signals()
