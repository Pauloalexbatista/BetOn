import sqlite3

conn = sqlite3.connect('beton.db')
cursor = conn.cursor()

# Get all teams
cursor.execute("SELECT id, name FROM teams ORDER BY name")
teams = cursor.fetchall()

print(f"Total teams: {len(teams)}\n")
print("All teams:")
for team_id, name in teams:
    print(f"  {team_id:3d}: {name}")

conn.close()
