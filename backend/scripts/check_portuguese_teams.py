import sqlite3

conn = sqlite3.connect('backend/beton.db')
cursor = conn.cursor()

print("Checking for Portuguese teams in BACKEND DB:\n")

teams_to_check = [
    'Sporting', 'Sp Lisbon', 'Sporting Clube de Portugal',
    'Benfica', 'Sport Lisboa e Benfica',
    'Porto', 'FC Porto',
    'SC Braga', 'Sp Braga', 'Sporting Clube de Braga'
]

for team_name in teams_to_check:
    cursor.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
    result = cursor.fetchone()
    
    if result:
        tid = result[0]
        cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (tid, tid))
        matches = cursor.fetchone()[0]
        print(f"✓ {team_name:40s} (ID {tid:3d}): {matches} matches")
    else:
        print(f"✗ {team_name:40s} NOT FOUND")

conn.close()
