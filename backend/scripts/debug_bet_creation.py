import requests
import json

def test_bet_creation():
    url = "http://localhost:8000/api/bets/"
    
    # Payload similar to frontend
    payload = {
        "match_id": 4873,  # ID from previous debug output (Sporting vs Benfica)
        "strategy_id": 3,  # 3 grandes individuais
        "market": "win",
        "selection": "win",
        "odds": 2.0,
        "stake": 10.0,
        "is_paper_trade": True
    }
    
    print(f"🚀 Sending payload to {url}:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bet_creation()
