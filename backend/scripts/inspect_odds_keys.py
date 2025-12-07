import sys
import os
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Odds, Match

def inspect_odds():
    db = SessionLocal()
    try:
        # Get last 10 odds entries
        odds_entries = db.query(Odds).order_by(Odds.id.desc()).limit(10).all()
        
        print(f"Inspecting {len(odds_entries)} recent odds entries...")
        
        for odd in odds_entries:
            print(f"\nID: {odd.id}, Bookmaker: {odd.bookmaker}, Market: {odd.market}")
            if odd.odds_data:
                print(f"Keys: {list(odd.odds_data.keys())}")
                print(f"Sample Data: {json.dumps(odd.odds_data)}")
            else:
                print("No Data")
                
    finally:
        db.close()

if __name__ == "__main__":
    inspect_odds()
