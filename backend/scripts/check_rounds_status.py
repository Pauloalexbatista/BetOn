import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def check_rounds():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- 2024/2025 Season Status ---")
    
    # Check total matches for season
    cursor.execute("SELECT COUNT(*) FROM matches WHERE league='Primeira Liga' AND season='2024/2025'")
    total = cursor.fetchone()[0]
    
    print(f"Total Matches: {total}")
    
    # Check Round Distribution
    cursor.execute("""
        SELECT round, COUNT(*) 
        FROM matches 
        WHERE league='Primeira Liga' AND season='2024/2025'
        GROUP BY round
        ORDER BY CAST(round AS INTEGER)
    """)
    rounds = cursor.fetchall()
    
    print(f"Round Distribution:")
    for r, count in rounds:
        print(f"  Round {r}: {count} matches")
        
    conn.close()

if __name__ == "__main__":
    check_rounds()
