import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def list_season_teams():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- 2025/2026 Teams ---")
    cursor.execute("""
        SELECT DISTINCT t.name 
        FROM matches m 
        JOIN teams t ON m.home_team_id=t.id 
        WHERE m.season='2025/2026' 
        AND m.league='Primeira Liga'
        ORDER BY t.name
    """)
    rows = cursor.fetchall()
    
    for r in rows:
        print(r[0])
        
    conn.close()

if __name__ == "__main__":
    list_season_teams()
