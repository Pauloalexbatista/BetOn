"""
FINAL team consolidation - Portuguese teams with foreign names
"""
import sqlite3

def final_consolidation():
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    print("🔧 FINAL Team Consolidation")
    print("=" * 60)
    
    # Get all teams first
    cursor.execute("SELECT id, name FROM teams ORDER BY name")
    all_teams = cursor.fetchall()
    
    print(f"\nCurrent teams ({len(all_teams)}):")
    for tid, tname in all_teams:
        cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (tid, tid))
        matches = cursor.fetchone()[0]
        print(f"  {tid:3d}: {tname:40s} ({matches} matches)")
    
    # Define ALL consolidations
    consolidations = [
        # Sporting variations → Sporting (ID 26)
        ('Sp Lisbon', 26, 'Sporting'),
        ('Sporting Clube de Portugal', 26, 'Sporting'),
        
        # Benfica variations → Benfica (ID 2)
        ('Sport Lisboa e Benfica', 2, 'Benfica'),
        
        # Braga variations → SC Braga (ID 4)
        ('Sp Braga', 4, 'SC Braga'),
        ('Sporting Clube de Braga', 4, 'SC Braga'),
    ]
    
    print(f"\n📋 Planned consolidations:")
    actual_consolidations = []
    
    for old_name, target_id, target_name in consolidations:
        cursor.execute("SELECT id FROM teams WHERE name = ?", (old_name,))
        result = cursor.fetchone()
        
        if result:
            old_id = result[0]
            cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (old_id, old_id))
            matches = cursor.fetchone()[0]
            
            print(f"  ✓ {old_name:40s} (ID {old_id:3d}, {matches:3d} matches) → {target_name} (ID {target_id})")
            actual_consolidations.append((old_name, old_id, target_id, target_name))
        else:
            print(f"  ✗ {old_name:40s} - NOT FOUND")
    
    if not actual_consolidations:
        print("\n✅ No consolidations needed!")
        conn.close()
        return
    
    print(f"\n⚠️  Will consolidate {len(actual_consolidations)} teams")
    response = input("Proceed? (YES to confirm): ")
    
    if response != 'YES':
        print("❌ Cancelled")
        conn.close()
        return
    
    for old_name, old_id, target_id, target_name in actual_consolidations:
        print(f"\n📌 {old_name} → {target_name}")
        
        # Update home matches
        cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (target_id, old_id))
        home_updated = cursor.rowcount
        
        # Update away matches
        cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (target_id, old_id))
        away_updated = cursor.rowcount
        
        # Delete old team
        cursor.execute("DELETE FROM teams WHERE id = ?", (old_id,))
        
        print(f"  ✅ Updated {home_updated} home + {away_updated} away = {home_updated + away_updated} total matches")
        print(f"  🗑️  Deleted ID {old_id}")
    
    conn.commit()
    
    # Final count
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Final team count: {final_count}")
    
    # Show final Portuguese teams
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
    print("\n✅ FINAL consolidation complete!")

if __name__ == "__main__":
    final_consolidation()
