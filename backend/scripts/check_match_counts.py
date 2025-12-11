import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def check_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT count(*) FROM matches WHERE league='Primeira Liga' AND season='2025/2026'")
    count = cursor.fetchone()[0]
    print(f"Primeira Liga 2025/2026 Matches: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_counts()
