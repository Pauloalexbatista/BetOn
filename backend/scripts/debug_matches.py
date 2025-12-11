import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def check_matches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Inspecting 2025/2026 Matches ---")
    cursor.execute("""
        SELECT m.id, h.name, a.name, m.match_date, m.round 
        FROM matches m 
        JOIN teams h ON m.home_team_id=h.id 
        JOIN teams a ON m.away_team_id=a.id 
        WHERE m.season='2025/2026' 
        AND m.league='Primeira Liga' 
        LIMIT 15
    """)
    rows = cursor.fetchall()
    
    for r in rows:
        print(r)
        
    conn.close()

if __name__ == "__main__":
    check_matches()
