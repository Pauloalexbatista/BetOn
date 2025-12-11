"""
Rename and consolidate Portuguese teams in backend database
"""
import sqlite3

def rename_and_consolidate():
    conn = sqlite3.connect('backend/beton.db')
    cursor = conn.cursor()
    
    print("🔧 Renaming and Consolidating Portuguese Teams")
    print("=" * 60)
    
    # Step 1: Rename main teams to Portuguese names
    renames = [
        ('Sp Lisbon', 'Sporting'),
        ('Sp Braga', 'SC Braga'),
    ]
    
    print("\n📝 Step 1: Renaming teams to Portuguese names")
    for old_name, new_name in renames:
        cursor.execute("SELECT id FROM teams WHERE name = ?", (old_name,))
        result = cursor.fetchone()
        
        if result:
            tid = result[0]
            cursor.execute("UPDATE teams SET name = ? WHERE id = ?", (new_name, tid))
            print(f"  ✅ Renamed: {old_name:40s} → {new_name}")
        else:
            print(f"  ⚠️  Not found: {old_name}")
    
    conn.commit()
    
    # Step 2: Consolidate variations into renamed teams
    consolidations = [
        ('Sporting Clube de Portugal', 'Sporting'),
        ('Sporting Clube de Braga', 'SC Braga'),
    ]
    
    print("\n📝 Step 2: Consolidating variations")
    
    for old_name, target_name in consolidations:
        # Find old team
        cursor.execute("SELECT id FROM teams WHERE name = ?", (old_name,))
        old_result = cursor.fetchone()
        
        if not old_result:
            print(f"  ⚠️  Not found: {old_name}")
            continue
        
        old_id = old_result[0]
        
        # Find target team
        cursor.execute("SELECT id FROM teams WHERE name = ?", (target_name,))
        target_result = cursor.fetchone()
        
        if not target_result:
            print(f"  ⚠️  Target not found: {target_name}")
            continue
        
        target_id = target_result[0]
        
        # Count matches
        cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (old_id, old_id))
        matches = cursor.fetchone()[0]
        
        print(f"  📌 {old_name:40s} → {target_name}")
        
        # Update matches
        cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (target_id, old_id))
        home_updated = cursor.rowcount
        
        cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (target_id, old_id))
        away_updated = cursor.rowcount
        
        # Delete old team
        cursor.execute("DELETE FROM teams WHERE id = ?", (old_id,))
        
        print(f"     ✅ Updated {home_updated + away_updated} matches, deleted ID {old_id}")
    
    conn.commit()
    
    # Final stats
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Final Results:")
    print(f"  Total teams: {final_count}")
    
    print(f"\n✅ Portuguese teams:")
    for name in ['Sporting', 'Benfica', 'Porto', 'SC Braga']:
        cursor.execute("SELECT id FROM teams WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            tid = result[0]
            cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (tid, tid))
            matches = cursor.fetchone()[0]
            print(f"  {name:15s} (ID {tid:3d}): {matches} matches")
    
    conn.close()
    print("\n✅ Complete!")

if __name__ == "__main__":
    rename_and_consolidate()
