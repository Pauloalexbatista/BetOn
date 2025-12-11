import sqlite3

conn = sqlite3.connect('beton.db')
cursor = conn.cursor()

# Search for all Portuguese team variations
search_terms = ['Sp', 'Sport', 'Lisbon', 'Lisboa', 'Portugal', 'Braga', 'Benfica', 'Porto']

print("Teams matching Portuguese keywords:\n")

for term in search_terms:
    cursor.execute(f"SELECT id, name FROM teams WHERE name LIKE '%{term}%' ORDER BY name")
    teams = cursor.fetchall()
    
    if teams:
        print(f"\n--- Containing '{term}' ---")
        for tid, tname in teams:
            cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (tid, tid))
            matches = cursor.fetchone()[0]
            print(f"  {tid:3d}: {tname:45s} ({matches} matches)")

conn.close()
