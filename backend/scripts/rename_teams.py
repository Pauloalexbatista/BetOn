"""
Script to rename teams to simpler, more user-friendly names
"""
import sqlite3

# Mapping of current names to simplified names
TEAM_RENAMES = {
    'Sp Lisbon': 'Sporting',
    'Sporting CP': 'Sporting',
    'SL Benfica': 'Benfica',
    'FC Porto': 'Porto'
}

def rename_teams(dry_run=True):
    """
    Rename teams to simpler names
    
    Args:
        dry_run: If True, only show what would be done
    """
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    print("🏷️  Team Rename Script")
    print("=" * 60)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print("=" * 60)
    
    for old_name, new_name in TEAM_RENAMES.items():
        # Check if team exists
        cursor.execute("SELECT id, name FROM teams WHERE name = ?", (old_name,))
        result = cursor.fetchone()
        
        if result:
            team_id, current_name = result
            
            # Count matches
            cursor.execute("""
                SELECT COUNT(*) FROM matches 
                WHERE home_team_id = ? OR away_team_id = ?
            """, (team_id, team_id))
            match_count = cursor.fetchone()[0]
            
            print(f"\n📌 {old_name} → {new_name}")
            print(f"   ID: {team_id}")
            print(f"   Matches: {match_count}")
            
            if not dry_run:
                cursor.execute("UPDATE teams SET name = ? WHERE id = ?", (new_name, team_id))
                print(f"   ✅ Renamed to: {new_name}")
        else:
            print(f"\n⚠️  Team '{old_name}' not found in database")
    
    if not dry_run:
        conn.commit()
        print("\n✅ All changes committed")
    else:
        print("\n⚠️  DRY RUN - No changes were made")
    
    # Show final team list
    cursor.execute("SELECT name FROM teams ORDER BY name")
    teams = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Final team list ({len(teams)} teams):")
    for team in teams:
        print(f"   - {team}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    execute = '--execute' in sys.argv
    
    if execute:
        print("⚠️  EXECUTING RENAME - This will modify the database!")
        response = input("Are you sure? Type 'YES' to continue: ")
        if response == 'YES':
            rename_teams(dry_run=False)
        else:
            print("❌ Cancelled")
    else:
        print("Running in DRY RUN mode...")
        print("Use --execute flag to actually apply changes")
        rename_teams(dry_run=True)
