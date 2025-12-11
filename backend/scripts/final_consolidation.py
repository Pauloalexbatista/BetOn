"""
Final team consolidation script
"""
import sqlite3

# Teams to consolidate
CONSOLIDATIONS = [
    {
        'keep_id': 2,  # Benfica
        'merge_names': ['Sport Lisboa e Benfica'],
        'canonical_name': 'Benfica'
    },
    {
        'keep_id': 26,  # Sporting (já consolidado antes)
        'merge_names': ['Sporting Clube de Portugal'],
        'canonical_name': 'Sporting'
    },
    {
        'keep_id': 4,  # SC Braga
        'merge_names': ['Sp Braga', 'Sporting Clube de Braga'],
        'canonical_name': 'SC Braga'
    }
]

def consolidate():
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    print("🔧 Final Team Consolidation")
    print("=" * 60)
    
    for config in CONSOLIDATIONS:
        keep_id = config['keep_id']
        canonical_name = config['canonical_name']
        
        print(f"\n📌 {canonical_name} (Keep ID: {keep_id})")
        
        for merge_name in config['merge_names']:
            # Find team by name
            cursor.execute("SELECT id, name FROM teams WHERE name = ?", (merge_name,))
            result = cursor.fetchone()
            
            if result:
                merge_id, current_name = result
                
                # Count matches
                cursor.execute("""
                    SELECT COUNT(*) FROM matches 
                    WHERE home_team_id = ? OR away_team_id = ?
                """, (merge_id, merge_id))
                match_count = cursor.fetchone()[0]
                
                print(f"   Found: {current_name} (ID: {merge_id}) - {match_count} matches")
                
                # Update matches
                cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (keep_id, merge_id))
                home_updated = cursor.rowcount
                
                cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (keep_id, merge_id))
                away_updated = cursor.rowcount
                
                # Delete duplicate
                cursor.execute("DELETE FROM teams WHERE id = ?", (merge_id,))
                
                print(f"   ✅ Merged: {home_updated} home + {away_updated} away matches")
                print(f"   🗑️  Deleted ID: {merge_id}")
            else:
                print(f"   ⚠️  Not found: {merge_name}")
        
        # Update canonical name
        cursor.execute("UPDATE teams SET name = ? WHERE id = ?", (canonical_name, keep_id))
        print(f"   ✅ Updated name to: {canonical_name}")
    
    conn.commit()
    
    # Show final count
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Final team count: {final_count}")
    
    # Show all teams
    cursor.execute("SELECT name FROM teams ORDER BY name")
    teams = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ All teams ({len(teams)}):")
    for team in teams:
        print(f"   - {team}")
    
    conn.close()
    print("\n✅ Consolidation complete!")

if __name__ == "__main__":
    consolidate()
