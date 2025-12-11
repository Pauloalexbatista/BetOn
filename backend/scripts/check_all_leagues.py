import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "beton.db")

def check_leagues():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- League Status Audit (2024/2025) ---")
    
    # Get distinct leagues
    cursor.execute("SELECT distinct league FROM matches WHERE season='2024/2025'")
    leagues = [r[0] for r in cursor.fetchall()]
    
    if not leagues:
        print("No leagues found for 2024/2025.")
        return

    for league in leagues:
        print(f"\nExample: {league}")
        
        # Count matches
        cursor.execute("SELECT COUNT(*) FROM matches WHERE league=? AND season='2024/2025'", (league,))
        total = cursor.fetchone()[0]
        
        # Count finished (with scores)
        cursor.execute("SELECT COUNT(*) FROM matches WHERE league=? AND season='2024/2025' AND home_score IS NOT NULL", (league,))
        finished = cursor.fetchone()[0]
        
        # Check rounds
        cursor.execute("SELECT round, COUNT(*) FROM matches WHERE league=? AND season='2024/2025' GROUP BY round ORDER BY CAST(round AS INTEGER)", (league,))
        rounds = cursor.fetchall()
        
        print(f"  Total Matches: {total}")
        print(f"  Finished Games: {finished} ({(finished/total*100 if total else 0):.1f}%)")
        print(f"  Rounds: {len(rounds)} active rounds")
        if rounds:
            # Print first 3 and last 3 rounds as sample
            print(f"    First: Round {rounds[0][0]} ({rounds[0][1]} games)")
            if len(rounds) > 1:
                print(f"    Last:  Round {rounds[-1][0]} ({rounds[-1][1]} games)")
        else:
            print("    No rounds defined.")

if __name__ == "__main__":
    check_leagues()
