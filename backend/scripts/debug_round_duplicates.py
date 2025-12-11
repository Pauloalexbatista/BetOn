import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "beton.db")

def debug_round(round_num):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"--- Debugging Round {round_num} ---")
    cursor.execute("""
        SELECT m.id, h.name, a.name, m.round, m.match_date, m.status, m.season
        FROM matches m
        JOIN teams h ON m.home_team_id = h.id
        JOIN teams a ON m.away_team_id = a.id
        WHERE m.round = ? AND m.season = '2025/2026' AND m.league = 'Primeira Liga'
    """, (str(round_num),))
    
    rows = cursor.fetchall()
    for r in rows:
        print(r)

if __name__ == "__main__":
    debug_round(3)
    debug_round(1)
