import sqlite3
import os
import math

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def infer_rounds():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Inferring Rounds for Primeira Liga 25/26 ---")
    
    # Get all matches ordered by date
    cursor.execute("""
        SELECT id, match_date, home_team_id, away_team_id 
        FROM matches 
        WHERE league='Primeira Liga' AND season='2025/2026'
        ORDER BY match_date, id
    """)
    matches = cursor.fetchall()
    
    total = len(matches)
    if total == 0:
        print("No matches found.")
        return

    # Assuming 18 teams -> 9 games per round
    GAMES_PER_ROUND = 9
    
    print(f"Total Matches: {total}")
    print(f"Expected Rounds: {total / GAMES_PER_ROUND}")
    
    updates = 0
    assigned_round = 1
    
    for i, match in enumerate(matches):
        match_id = match[0]
        
        # Calculate round (1-based)
        # i=0..8 -> Round 1
        # i=9..17 -> Round 2
        assigned_round = (i // GAMES_PER_ROUND) + 1
        
        cursor.execute("UPDATE matches SET round = ? WHERE id = ?", (str(assigned_round), match_id))
        updates += 1
        
    conn.commit()
    conn.close()
    print(f"✅ Updated {updates} matches with inferred rounds (1-{assigned_round}).")

if __name__ == "__main__":
    infer_rounds()
