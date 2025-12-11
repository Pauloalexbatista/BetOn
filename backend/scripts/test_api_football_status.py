"""
Test API-Football connection and check quota status
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.api_football import APIFootballClient
from config import get_settings

def main():
    print("🔍 Testing API-Football Connection...\n")
    
    settings = get_settings()
    
    # Check if key is configured
    if not settings.api_football_key or settings.api_football_key == "":
        print("❌ API-Football key NOT configured!")
        print("📝 Please add API_FOOTBALL_KEY to your .env file")
        return
    
    print(f"✅ API Key found: {settings.api_football_key[:10]}...")
    
    # Initialize client
    client = APIFootballClient()
    
    # Check API status and quota
    print("\n📊 Checking API Status and Quota...")
    status = client.get_status()
    
    if status.get("errors"):
        print(f"❌ Error: {status['errors']}")
        return
    
    # Display quota info
    if status.get("response"):
        account = status["response"]["account"]
        requests = status["response"]["requests"]
        
        print("\n✅ API-Football Connected Successfully!")
        print(f"\n👤 Account: {account.get('firstname', 'N/A')} {account.get('lastname', 'N/A')}")
        print(f"📧 Email: {account.get('email', 'N/A')}")
        
        print(f"\n📈 Quota Status:")
        print(f"   • Limit (day): {requests.get('limit_day', 'N/A')}")
        print(f"   • Current: {requests.get('current', 'N/A')}")
        print(f"   • Remaining: {requests.get('limit_day', 0) - requests.get('current', 0)}")
        
        # Test fetching Primeira Liga
        print("\n🇵🇹 Testing Primeira Liga Data...")
        leagues = client.get_leagues(country="Portugal")
        
        if leagues:
            print(f"✅ Found {len(leagues)} Portuguese leagues:")
            for league in leagues[:3]:  # Show first 3
                league_info = league.get("league", {})
                print(f"   • {league_info.get('name')} (ID: {league_info.get('id')})")
        else:
            print("❌ No leagues found")
    else:
        print("❌ Unexpected response format")
        print(status)

if __name__ == "__main__":
    main()
