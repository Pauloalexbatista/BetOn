"""
Script to check for duplicate team names in the database
"""
import sqlite3
from collections import Counter

def check_duplicates():
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("📊 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check teams table schema
    cursor.execute("PRAGMA table_info(teams)")
    columns = cursor.fetchall()
    print("\n📋 Teams table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Get all teams from teams table
    cursor.execute("SELECT id, name FROM teams ORDER BY name")
    teams_data = cursor.fetchall()
    
    print(f"\n🏆 Total teams in database: {len(teams_data)}")
    print("\n📝 All teams:")
    for team_id, team_name in teams_data:
        print(f"  [{team_id}] {team_name}")
    
    # Check for potential duplicates (similar names)
    print("\n⚠️  Potential duplicates (similar names):")
    checked = set()
    duplicates_found = []
    
    for team_id, team_name in teams_data:
        # Normalize name for comparison
        normalized = team_name.lower().strip()
        base_name = normalized.replace(' fc', '').replace(' cf', '').replace('fc ', '').replace('cf ', '')
        
        # Find similar team names
        similar = []
        for other_id, other_name in teams_data:
            if other_id == team_id:
                continue
            other_normalized = other_name.lower().strip()
            other_base = other_normalized.replace(' fc', '').replace(' cf', '').replace('fc ', '').replace('cf ', '')
            
            # Check if base names match
            if base_name == other_base or base_name in other_base or other_base in base_name:
                similar.append((other_id, other_name))
        
        if similar and team_name not in checked:
            print(f"\n  🔴 {team_name} (ID: {team_id}):")
            for s_id, s_name in similar:
                print(f"      ↔️  {s_name} (ID: {s_id})")
                checked.add(s_name)
            checked.add(team_name)
            duplicates_found.append({
                'main': (team_id, team_name),
                'duplicates': similar
            })
    
    conn.close()

if __name__ == "__main__":
    check_duplicates()
