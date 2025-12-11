"""
Test ZeroZero Collector
Quick test to verify scraping works
"""

import sys
sys.path.append('..')

from collectors.zerozero_collector import ZeroZeroCollector
from database.session import get_db


def test_fetch_round():
    """Test fetching a single round"""
    db = next(get_db())
    collector = ZeroZeroCollector(db)
    
    print("🔍 Testing ZeroZero scraper...")
    print("\n1️⃣ Fetching Jornada 13...")
    
    matches = collector.fetch_round_matches("liga-portuguesa", 13)
    
    print(f"\n✅ Found {len(matches)} matches:")
    for match in matches[:5]:  # Show first 5
        date_str = match['date'].strftime('%d/%m') if match['date'] else 'TBD'
        score = f"{match['home_score']}-{match['away_score']}" if match['home_score'] is not None else "vs"
        print(f"  {date_str}: {match['home_team']} {score} {match['away_team']}")
    
    db.close()
    return matches


def test_fetch_all_rounds():
    """Test fetching all rounds"""
    db = next(get_db())
    collector = ZeroZeroCollector(db)
    
    print("\n2️⃣ Fetching all rounds...")
    
    rounds_data = collector.fetch_league_rounds("liga-portuguesa")
    
    print(f"\n✅ Found {len(rounds_data)} rounds")
    for round_info in rounds_data[:3]:  # Show first 3
        print(f"  Jornada {round_info['round']}: {len(round_info['matches'])} matches")
    
    db.close()
    return rounds_data


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ZeroZero Collector Test")
    print("=" * 60)
    
    # Test single round
    matches = test_fetch_round()
    
    # Test all rounds (commented out for speed)
    # rounds = test_fetch_all_rounds()
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
