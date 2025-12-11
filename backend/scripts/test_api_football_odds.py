from collectors.api_football import APIFootballClient

def test_api_football():
    print("=== API-FOOTBALL - Capabilities Test ===\n")
    
    client = APIFootballClient()
    
    # Test 1: Check quota/status
    print("1. Account Status:")
    status = client.get_status()
    
    if 'response' in status and status['response']:
        data = status['response']
        
        # Quota info
        requests = data.get('requests', {})
        print(f"   Daily Limit: {requests.get('limit_day', 'Unknown')}")
        print(f"   Used Today: {requests.get('current', 'Unknown')}")
        remaining = requests.get('limit_day', 0) - requests.get('current', 0)
        print(f"   Remaining: {remaining}")
        
        # Account info
        account = data.get('account', {})
        print(f"\n   Plan: {data.get('subscription', {}).get('plan', 'Unknown')}")
    else:
        print(f"   ❌ Error: {status.get('errors', 'Unknown')}")
    
    # Test 2: Try to get odds for Primeira Liga
    print("\n2. Testing Odds Endpoint:")
    print("   Attempting to get odds for Primeira Liga (league_id=94, season=2024)...")
    
    odds_response = client.get_odds(league_id=94, season=2024, page=1)
    
    if 'response' in odds_response:
        odds_list = odds_response.get('response', [])
        print(f"   ✅ Found {len(odds_list)} fixtures with odds")
        
        if len(odds_list) > 0:
            sample = odds_list[0]
            print(f"\n   Sample fixture:")
            fixture = sample.get('fixture', {})
            print(f"     ID: {fixture.get('id')}")
            print(f"     Date: {fixture.get('date')}")
            
            # Check bookmakers
            bookmakers = sample.get('bookmakers', [])
            print(f"     Bookmakers available: {len(bookmakers)}")
            if len(bookmakers) > 0:
                print(f"     Sample bookmaker: {bookmakers[0].get('name')}")
        else:
            print("   ⚠️ No odds found (may require paid plan)")
    
    elif 'errors' in odds_response:
        errors = odds_response.get('errors', {})
        print(f"   ❌ Error: {errors}")
        if 'requests' in str(errors).lower() or 'quota' in str(errors).lower():
            print("   ℹ️ This may indicate quota exhausted or endpoint not available in free tier")
    
    print("\n" + "="*60)
    print("CONCLUSION:")
    print("  - API-Football may provide historical odds")
    print("  - BUT: Often restricted to paid plans")
    print("  - Free tier: Limited requests/day")
    print("  - Need to check actual response to confirm availability")
    print("="*60)

if __name__ == "__main__":
    test_api_football()
