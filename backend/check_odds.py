import sqlite3

try:
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    # Count Odds
    cursor.execute("SELECT COUNT(*) FROM odds")
    odds_count = cursor.fetchone()[0]
    
    # Count Matches
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    
    print(f"Matches: {match_count}")
    print(f"Odds Records: {odds_count}")
    
    if odds_count > 0:
        cursor.execute("SELECT odds_data FROM odds LIMIT 1")
        print(f"Sample Odds: {cursor.fetchone()[0][:100]}...")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
