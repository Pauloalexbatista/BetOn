"""
Consolidate duplicates in BACKEND database
"""
import sqlite3

# Team name mapping
TEAM_NAME_MAP = {
    "Sp Lisbon": "Sporting",
    "Sporting Clube de Portugal": "Sporting",
    "Sporting CP": "Sporting",
    "Sport Lisboa e Benfica": "Benfica",
    "SL Benfica": "Benfica",
    "FC Porto": "Porto",
    "Sp Braga": "SC Braga",
    "Sporting Clube de Braga": "SC Braga",
    "Sporting Braga": "SC Braga",
}

def consolidate_backend_db():
    conn = sqlite3.connect('backend/beton.db')
    cursor = conn.cursor()
    
    print("🔧 Consolidating BACKEND Database")
    print("=" * 60)
    
    # Find teams that need consolidation
    consolidations = {}
    
    for old_name, target_name in TEAM_NAME_MAP.items():
        # Find old team
        cursor.execute("SELECT id FROM teams WHERE name = ?", (old_name,))
        old_result = cursor.fetchone()
        
        if not old_result:
            continue
            
        old_id = old_result[0]
        
        # Find target team
        cursor.execute("SELECT id FROM teams WHERE name = ?", (target_name,))
        target_result = cursor.fetchone()
        
        if target_result:
            target_id = target_result[0]
            if old_id != target_id:
                consolidations[old_id] = (old_name, target_name, target_id)
    
    if not consolidations:
        print("\n✅ No consolidations needed!")
        conn.close()
        return
    
    print(f"\n📋 Found {len(consolidations)} teams to consolidate:")
    for old_id, (old_name, target_name, target_id) in consolidations.items():
        cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (old_id, old_id))
        matches = cursor.fetchone()[0]
        print(f"  {old_name:40s} (ID {old_id:3d}, {matches:3d} matches) → {target_name} (ID {target_id})")
    
    print(f"\n⚠️  This will modify backend/beton.db")
    response = input("Proceed? (YES to confirm): ")
    
    if response != 'YES':
        print("❌ Cancelled")
        conn.close()
        return
    
    total_matches = 0
    
    for old_id, (old_name, target_name, target_id) in consolidations.items():
        print(f"\n📌 {old_name} → {target_name}")
        
        # Update matches
        cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (target_id, old_id))
        home_updated = cursor.rowcount
        
        cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (target_id, old_id))
        away_updated = cursor.rowcount
        
        total = home_updated + away_updated
        total_matches += total
        
        # Delete old team
        cursor.execute("DELETE FROM teams WHERE id = ?", (old_id,))
        
        print(f"  ✅ Updated {total} matches")
        print(f"  🗑️  Deleted ID {old_id}")
    
    conn.commit()
    
    # Final stats
    cursor.execute("SELECT COUNT(*) FROM teams")
    final_count = cursor.fetchone()[0]
    
    print(f"\n📊 Results:")
    print(f"  Teams consolidated: {len(consolidations)}")
    print(f"  Matches updated: {total_matches}")
    print(f"  Final team count: {final_count}")
    
    # Show Portuguese teams
    print(f"\n✅ Portuguese teams in BACKEND DB:")
    for name in ['Sporting', 'Benfica', 'Porto', 'SC Braga']:
        cursor.execute("SELECT id FROM teams WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            tid = result[0]
            cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ? OR away_team_id = ?", (tid, tid))
            matches = cursor.fetchone()[0]
            print(f"  {name:15s} (ID {tid:3d}): {matches} matches")
    
    conn.close()
    print("\n✅ Backend database consolidated!")

if __name__ == "__main__":
    consolidate_backend_db()
