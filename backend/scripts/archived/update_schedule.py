"""
Update Schedule - Fetch all remaining matches for the season
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collectors.schedule_collector import ScheduleCollector
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == "__main__":
    print("=" * 60)
    print("BetOn - Schedule Update")
    print("=" * 60)
    print()
    
    collector = ScheduleCollector()
    collector.sync_upcoming()  # No days parameter = fetch full season
    
    print()
    print("=" * 60)
    print("Schedule update complete!")
    print("=" * 60)
