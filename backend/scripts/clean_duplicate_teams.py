"""
Clean Duplicate Teams Script
Finds and merges duplicate team entries from different data sources
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match
from sqlalchemy import or_, func

def find_duplicates():
    """Find teams with similar names"""
    db = SessionLocal()
    
    teams = db.query(Team).order_by(Team.name).all()
    duplicates = {}
    
    # Group by base name (removing FC, AC, etc.)
    for team in teams:
        base_name = (team.name
                    .replace(' FC', '')
                    .replace(' AC', '')
                    .replace(' SC', '')
                    .replace(' CF', '')
                    .strip())
        
        if base_name not in duplicates:
            duplicates[base_name] = []
        duplicates[base_name].append(team)
    
    # Show duplicates with match counts
    print("\n🔍 EQUIPAS DUPLICADAS ENCONTRADAS:\n")
    print("=" * 80)
    
    found_duplicates = False
    for base, team_list in duplicates.items():
        if len(team_list) > 1:
            found_duplicates = True
            print(f"\n📌 {base}:")
            for t in team_list:
                home_count = db.query(Match).filter(Match.home_team_id == t.id).count()
                away_count = db.query(Match).filter(Match.away_team_id == t.id).count()
                total = home_count + away_count
                print(f"   - ID {t.id:3d}: {t.name:30s} ({total:3d} jogos)")
    
    if not found_duplicates:
        print("\n✅ Nenhum duplicado encontrado!")
    
    print("\n" + "=" * 80)
    db.close()
    return duplicates

def merge_teams(keep_id: int, remove_ids: list):
    """Merge duplicate teams into one"""
    db = SessionLocal()
    
    try:
        # Get team names for confirmation
        keep_team = db.query(Team).filter(Team.id == keep_id).first()
        remove_teams = db.query(Team).filter(Team.id.in_(remove_ids)).all()
        
        print(f"\n🔄 MERGING:")
        print(f"   KEEP: {keep_team.name} (ID {keep_id})")
        print(f"   REMOVE:")
        for t in remove_teams:
            print(f"      - {t.name} (ID {t.id})")
        
        # Update home matches
        home_updated = db.query(Match).filter(
            Match.home_team_id.in_(remove_ids)
        ).update({Match.home_team_id: keep_id}, synchronize_session=False)
        
        # Update away matches
        away_updated = db.query(Match).filter(
            Match.away_team_id.in_(remove_ids)
        ).update({Match.away_team_id: keep_id}, synchronize_session=False)
        
        # Delete duplicate teams
        deleted = db.query(Team).filter(Team.id.in_(remove_ids)).delete(synchronize_session=False)
        
        db.commit()
        
        print(f"\n✅ SUCESSO:")
        print(f"   - {home_updated} jogos em casa atualizados")
        print(f"   - {away_updated} jogos fora atualizados")
        print(f"   - {deleted} equipas removidas")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERRO: {e}")
    finally:
        db.close()

def auto_merge_obvious_duplicates():
    """Automatically merge obvious duplicates"""
    duplicates = find_duplicates()
    
    print("\n\n🤖 AUTO-MERGE DE DUPLICADOS ÓBVIOS:\n")
    print("=" * 80)
    
    db = SessionLocal()
    merged_count = 0
    
    for base, team_list in duplicates.items():
        if len(team_list) <= 1:
            continue
        
        # Find team with most matches
        best_team = None
        best_count = 0
        
        for t in team_list:
            count = db.query(Match).filter(
                or_(Match.home_team_id == t.id, Match.away_team_id == t.id)
            ).count()
            
            if count > best_count:
                best_count = count
                best_team = t
        
        # Merge others into best
        if best_team and best_count > 0:
            remove_ids = [t.id for t in team_list if t.id != best_team.id]
            if remove_ids:
                merge_teams(best_team.id, remove_ids)
                merged_count += 1
    
    db.close()
    
    print(f"\n\n✅ Total de grupos merged: {merged_count}")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "find":
            find_duplicates()
        elif sys.argv[1] == "auto":
            auto_merge_obvious_duplicates()
        elif sys.argv[1] == "merge" and len(sys.argv) >= 4:
            keep_id = int(sys.argv[2])
            remove_ids = [int(x) for x in sys.argv[3:]]
            merge_teams(keep_id, remove_ids)
        else:
            print("Uso:")
            print("  python clean_duplicate_teams.py find")
            print("  python clean_duplicate_teams.py auto")
            print("  python clean_duplicate_teams.py merge <keep_id> <remove_id1> [remove_id2 ...]")
    else:
        # Default: find duplicates
        find_duplicates()
