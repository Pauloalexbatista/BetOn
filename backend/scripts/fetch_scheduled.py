"""
Fetch scheduled matches from ZeroZero.pt
"""
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from collectors.zerozero_collector import ZeroZeroCollector

def main():
    db = SessionLocal()
    try:
        collector = ZeroZeroCollector(db)
        
        print("🔍 Fetching Primeira Liga from ZeroZero.pt...")
        print("=" * 50)
        
        # Fetch all rounds
        rounds_data = collector.fetch_league_rounds("liga-portuguesa")
        
        print(f"\n📊 Found {len(rounds_data)} rounds")
        
        # Show summary
        scheduled_count = 0
        finished_count = 0
        
        for round_info in rounds_data:
            for match in round_info['matches']:
                if match['status'] == 'scheduled':
                    scheduled_count += 1
                else:
                    finished_count += 1
        
        print(f"   Finished: {finished_count}")
        print(f"   Scheduled: {scheduled_count}")
        
        # Update database
        if rounds_data:
            print("\n💾 Updating database...")
            collector.update_database(rounds_data, "Primeira Liga")
            print("✅ Done!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
