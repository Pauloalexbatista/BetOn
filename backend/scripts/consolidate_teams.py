import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

# Mapping: { "Bad Team Name": "Target Team Name" }
# We will look up IDs dynamically to be safe
CONSOLIDATION_MAP = {
    "FC Arouca": "Arouca",
    "GD Estoril Praia": "Estoril",
    "CF Estrela da Amadora": "Estrela",
    "FC Famalicão": "Famalicao",
    "FC FamalicÒo": "Famalicao", # Handle encoding error version if present
    "SC Farense": "Farense",
    "Vitória Guimarães": "Guimaraes",
    "Vit¾ria GuimarÒes": "Guimaraes", # Handle encoding error version if present
    "CD Nacional": "Nacional",
    "CD Santa Clara": "Santa Clara",
    "Casa Pia AC": "Casa Pia" # Just in case
}

def consolidate_teams():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    print(f"--- Consolidating Teams in: {DB_PATH} ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        updated_matches = 0
        deleted_teams = 0

        for bad_name, target_name in CONSOLIDATION_MAP.items():
            print(f"\nProcessing: '{bad_name}' -> '{target_name}'")
            
            # 1. Get Target ID
            cursor.execute("SELECT id FROM teams WHERE name = ?", (target_name,))
            target_res = cursor.fetchone()
            
            if not target_res:
                print(f"  ❌ Target team '{target_name}' not found! Skipping.")
                continue
                
            target_id = target_res[0]
            print(f"  ✅ Target ID: {target_id}")

            # 2. Get Bad ID(s) - could be multiple if encoding weirdness matches differently? 
            # Usually unique name constraint, but let's be safe.
            cursor.execute("SELECT id FROM teams WHERE name = ?", (bad_name,))
            bad_matches = cursor.fetchall()
            
            if not bad_matches:
                print(f"  ℹ️  Bad team '{bad_name}' not found. Already cleaned?")
                continue
                
            for (bad_id,) in bad_matches:
                print(f"  Found duplicate team ID: {bad_id}")
                
                # 3. Update Home Matches
                cursor.execute("UPDATE matches SET home_team_id = ? WHERE home_team_id = ?", (target_id, bad_id))
                home_updates = cursor.rowcount
                
                # 4. Update Away Matches
                cursor.execute("UPDATE matches SET away_team_id = ? WHERE away_team_id = ?", (target_id, bad_id))
                away_updates = cursor.rowcount
                
                print(f"  Moved matches: {home_updates} (Home) + {away_updates} (Away)")
                updated_matches += (home_updates + away_updates)
                
                # 5. Delete Bad Team
                cursor.execute("DELETE FROM teams WHERE id = ?", (bad_id,))
                print(f"  🗑️  Deleted team ID {bad_id}")
                deleted_teams += 1

        conn.commit()
        print(f"\n--- Consolidation Complete ---")
        print(f"Total Matches Moved: {updated_matches}")
        print(f"Total Teams Deleted: {deleted_teams}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    consolidate_teams()
