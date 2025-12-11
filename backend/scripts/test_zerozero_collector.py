"""
Test ZeroZero collector and check data quality for current season
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.zerozero_collector import ZeroZeroCollector
from database.database import SessionLocal

def main():
    print("🔍 Testing ZeroZero Collector for 2024/25 Season\n")
    
    db = SessionLocal()
    collector = ZeroZeroCollector(db)
    
    print("📊 Fetching Sample Round Data...")
    print("   (Testing Round 13 as example)\n")
    
    # Test fetch one round
    round_matches = collector.fetch_round_matches("liga-portuguesa", 13)
    
    if round_matches:
        print(f"✅ Found {len(round_matches)} matches for Round 13\n")
        
        print("Sample matches:")
        for i, match in enumerate(round_matches[:5], 1):
            home = match.get('home_team', '?')
            away = match.get('away_team', '?')
            date = match.get('date', 'No date')
            home_score = match.get('home_score', '-')
            away_score = match.get('away_score', '-')
            status = match.get('status', 'unknown')
            
            scores = f"{home_score}-{away_score}" if home_score is not None else "vs"
            print(f"   {i}. {home} {scores} {away}")
            print(f"      Date: {date} | Status: {status}")
    else:
        print("❌ No matches found - scraper may be broken!")
        print("   Possible reasons:")
        print("   - ZeroZero changed their HTML structure")
        print("   - Network issues")
        print("   - Incorrect league/round identifier")
    
    # Test fetching all rounds (dry run - no DB update)
    print("\n\n📅 Testing Full Season Fetch (Dry Run)...")
    print("   (This will test if we can access all 34 rounds)\n")
    
    rounds_data = collector.fetch_league_rounds("liga-portuguesa")
    
    if rounds_data:
        print(f"✅ Successfully accessed {len(rounds_data)} rounds")
        
        total_matches = sum(len(r.get('matches', [])) for r in rounds_data)
        print(f"✅ Total matches found: {total_matches}")
        
        # Show sample from first and last round
        if rounds_data:
            first_round = rounds_data[0]
            last_round = rounds_data[-1]
            
            print(f"\n📊 First Round ({first_round.get('round')}):")
            for match in first_round.get('matches', [])[:3]:
                print(f"   • {match.get('home_team')} vs {match.get('away_team')}")
            
            print(f"\n📊 Last Round ({last_round.get('round')}):")
            for match in last_round.get('matches', [])[:3]:
                print(f"   • {match.get('home_team')} vs {match.get('away_team')}")
    else:
        print("❌ Failed to fetch rounds data")
    
    # Check data quality
    print("\n\n🔍 Data Quality Check:")
    
    if rounds_data:
        rounds_with_dates = sum(1 for r in rounds_data if any(m.get('date') for m in r.get('matches', [])))
        rounds_with_scores = sum(1 for r in rounds_data if any(m.get('home_score') is not None for m in r.get('matches', [])))
        
        print(f"   ✅ Rounds with dates: {rounds_with_dates}/{len(rounds_data)}")
        print(f"   ✅ Rounds with scores: {rounds_with_scores}/{len(rounds_data)}")
        
        if rounds_with_dates == 0:
            print("   ⚠️  WARNING: No dates found - scraper needs fixing!")
        
        if rounds_with_scores < len(rounds_data) / 2:
            print("   ℹ️  INFO: Many rounds without scores (likely future matches)")
    
    db.close()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSION:")
    print("="*60)
    if rounds_data and len(rounds_data) >= 30:
        print("✅ ZeroZero collector is WORKING")
        print("✅ Can be used for current season data")
        print("⚠️  But: No odds data (need separate odds source)")
    else:
        print("❌ ZeroZero collector needs debugging")
        print("   → Will need to fix HTML parsing")
    print("="*60)

if __name__ == "__main__":
    main()
