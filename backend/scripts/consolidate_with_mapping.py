"""
Consolidate existing duplicate teams based on new mapping
"""
import sqlite3

# Same mapping as in collector
TEAM_NAME_MAP = {
    # Sporting variations
    "Sp Lisbon": "Sporting",
    "Sporting Clube de Portugal": "Sporting",
    "Sporting CP": "Sporting",
    
    # Benfica variations
    "Sport Lisboa e Benfica": "Benfica",
    "SL Benfica": "Benfica",
    
    # Porto variations
    "FC Porto": "Porto",
    
    # Braga variations
    "Sp Braga": "SC Braga",
    "Sporting Clube de Braga": "SC Braga",
    "Sporting Braga": "SC Braga",
}

def consolidate():
    conn = sqlite3.connect('beton.db')
    cursor = conn.cursor()
    
    print("🔧 Consolidating Duplicate Teams")
    print("=" * 60)
    
    # Get all teams
    cursor.execute("SELECT id, name FROM teams ORDER BY name")
    all_teams = cursor.fetchall()
    
    print(f"\nCurrent teams: {len(all_teams)}")
    
    # Find teams that need consolidation
    consolidations = {}  # old_id -> (old_name, target_name, target_id)
    
    for team_id, team_name in all_teams:
        if team_name in TEAM_NAME_MAP:
            target_name = TEAM_NAME_MAP[team_name]
            
            # Find target team
            cursor.execute("SELECT id FROM teams WHERE name = ?", (target_name,))
            result = cursor.fetchone()
            
            if result:
                target_id = result[0]
                if target_id != team_id:  # Don't consolidate with self
                    consolidations[team_id] = (team_name, target_name, target_id)
    
    if not consolidations:
        print("\n✅ No duplicates to consolidate!")
        conn.close()
        return
    
    print(f"\n📋 Found {len(consolidations)} teams to consolidate:")
    for old_id, (old_name, target_name, target_id) in consolidations.items():
        cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (old_id, old_id))
        matches = cursor.fetchone()[0]
        print(f"  {old_name:40s} (ID {old_id:3d}, {matches:3d} matches) → {target_name} (ID {target_id})")
    
    response = input("\nProceed? (YES to confirm): ")
    
    if response != 'YES':
        print("❌ Cancelled")
        conn.close()
        return
    
    total_matches_updated = 0
    
    for old_id, (old_name, target_name, target_id) in consolidations.items():
        print(f"\n📌 {old_name} → {target_name}")
        
        # Update matches
        cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (target_id, old_id))
        home_updated = cursor.rowcount
        
        cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (target_id, old_id))
        away_updated = cursor.rowcount
        
        total = home_updated + away_updated
        total_matches_updated += total
        
        # Delete old team
        cursor.execute("DELETE FROM teams WHERE id = ?", (old_id,))
        
        print(f"  ✅ Updated {total} matches")
        print(f"  🗑️  Deleted ID {old_id}")
    
    conn.commit()
    
    # Final stats
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Results:")
    print(f"  Final team count: {final_count}")
    print(f"  Total matches updated: {total_matches_updated}")
    
    # Show Portuguese teams
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
    print("\n✅ Consolidation complete!")

if __name__ == "__main__":
    consolidate()
