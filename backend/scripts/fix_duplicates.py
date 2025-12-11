"""
Final team name cleanup
"""
import sqlite3

def check_and_fix():
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    print("🔍 Checking for duplicate team names...")
    print("=" * 60)
    
    # Find all teams with Sporting, Benfica, or Lisbon in name
    cursor.execute("""
        SELECT id, name FROM teams 
        WHERE name LIKE '%Sporting%' 
           OR name LIKE '%Benfica%' 
           OR name LIKE '%Lisbon%'
        ORDER BY name
    """)
    
    teams = cursor.fetchall()
    
    print(f"\nFound {len(teams)} teams:")
    for team_id, name in teams:
        cursor.execute("""
            SELECT COUNT(*) FROM matches 
            WHERE home_team_id = ? OR away_team_id = ?
        """, (team_id, team_id))
        match_count = cursor.fetchone()[0]
        print(f"  ID {team_id:3d}: {name:40s} ({match_count} matches)")
    
    # Define consolidations
    consolidations = []
    
    # Find Sp Lisbon
    cursor.execute("SELECT id FROM teams WHERE name = 'Sp Lisbon'")
    sp_lisbon = cursor.fetchone()
    
    # Find Sporting Clube de Portugal
    cursor.execute("SELECT id FROM teams WHERE name = 'Sporting Clube de Portugal'")
    sporting_portugal = cursor.fetchone()
    
    # Find Sporting (target)
    cursor.execute("SELECT id FROM teams WHERE name = 'Sporting'")
    sporting = cursor.fetchone()
    
    # Find Sport Lisboa e Benfica
    cursor.execute("SELECT id FROM teams WHERE name = 'Sport Lisboa e Benfica'")
    sport_benfica = cursor.fetchone()
    
    # Find Benfica (target)
    cursor.execute("SELECT id FROM teams WHERE name = 'Benfica'")
    benfica = cursor.fetchone()
    
    if sp_lisbon and sporting:
        consolidations.append(('Sp Lisbon', sp_lisbon[0], 'Sporting', sporting[0]))
    
    if sporting_portugal and sporting:
        consolidations.append(('Sporting Clube de Portugal', sporting_portugal[0], 'Sporting', sporting[0]))
    
    if sport_benfica and benfica:
        consolidations.append(('Sport Lisboa e Benfica', sport_benfica[0], 'Benfica', benfica[0]))
    
    if not consolidations:
        print("\n✅ No duplicates found!")
        conn.close()
        return
    
    print(f"\n🔧 Will consolidate {len(consolidations)} duplicates:")
    for old_name, old_id, new_name, new_id in consolidations:
        print(f"  {old_name} (ID {old_id}) → {new_name} (ID {new_id})")
    
    response = input("\nProceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled")
        conn.close()
        return
    
    for old_name, old_id, new_name, new_id in consolidations:
        print(f"\n📌 Consolidating {old_name}...")
        
        # Update matches
        cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (new_id, old_id))
        home_updated = cursor.rowcount
        
        cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (new_id, old_id))
        away_updated = cursor.rowcount
        
        # Delete old team
        cursor.execute("DELETE FROM teams WHERE id = ?", (old_id,))
        
        print(f"  ✅ Updated {home_updated} home + {away_updated} away matches")
        print(f"  🗑️  Deleted ID {old_id}")
    
    conn.commit()
    
    # Show final count
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Final team count: {final_count}")
    
    conn.close()
    print("\n✅ Consolidation complete!")

if __name__ == "__main__":
    check_and_fix()
