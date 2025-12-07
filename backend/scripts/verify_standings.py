
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from analysis.standings import StandingsEngine

def verify_standings():
    db = SessionLocal()
    engine = StandingsEngine(db)
    
    # Test Case: Liga Portugal 2014/2015 (if we had specific data, but we have 23/24)
    # Let's test 2023/2024 Final Table (approx May 2024)
    # vs Mid-Season (Dec 2023)
    
    league = "Primeira Liga"
    season = "2023/2024"
    
    print(f"\n🚀 Verifying Standard 'Time Travel'")
    print(f"League: {league} | Season: {season}")
    
    # Snapshot 1: Christmas Number One (25th Dec 2023)
    date_1 = datetime(2023, 12, 25).date()
    table_xmas = engine.calculate_table(league, season, as_of_date=date_1)
    
    print(f"\n🎄 Christmas Standings ({date_1}):")
    print_top_5(table_xmas)
    
    # Snapshot 2: Final Table (30th May 2024)
    date_2 = datetime(2024, 5, 30).date()
    table_final = engine.calculate_table(league, season, as_of_date=date_2)
    
    print(f"\n🏆 Final Standings ({date_2}):")
    print_top_5(table_final)

def print_top_5(table):
    print(f"{'Pos':<4} {'Team':<20} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'Pts':<4}")
    print("-" * 50)
    for row in table[:5]:
        print(f"{row['position']:<4} {row['team']:<20} {row['played']:<3} {row['won']:<3} {row['drawn']:<3} {row['lost']:<3} {row['points']:<4}")

if __name__ == "__main__":
    verify_standings()
