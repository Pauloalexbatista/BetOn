"""
OpenFootball Data Sync - FREE Public Domain Football Data
No API key required!
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collectors.openfootball_collector import OpenFootballCollector
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == "__main__":
    print("=" * 60)
    print("OpenFootball Data Collector")
    print("FREE - Public Domain - No API Key Required!")
    print("Source: https://github.com/openfootball/football.json")
    print("=" * 60)
    print()
    
    collector = OpenFootballCollector()
    
    # Sync Primeira Liga 2024/25
    print("Syncing Primeira Liga 2024/25...")
    collector.sync_league("Primeira Liga")
    
    print()
    print("=" * 60)
    print("✅ Done! Check your database for new matches!")
    print("=" * 60)
