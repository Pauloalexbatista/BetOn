import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def audit_teams():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    print(f"--- Auditing Database: {DB_PATH} ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all teams ordered by League then Name
        cursor.execute("SELECT id, name, league, country FROM teams ORDER BY league, name")
        teams = cursor.fetchall()
        
        print(f"Total Teams found: {len(teams)}\n")
        
        # Group by League
        current_league = None
        for team in teams:
            t_id, name, league, country = team
            
            if league != current_league:
                current_league = league
                print(f"\n=== {current_league} ===")
                print(f"{'ID':<5} | {'Name':<30} | {'Matches (Home/Away)'}")
                print("-" * 60)
            
            # Count matches
            cursor.execute("SELECT COUNT(*) FROM matches WHERE home_team_id = ?", (t_id,))
            home_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM matches WHERE away_team_id = ?", (t_id,))
            away_count = cursor.fetchone()[0]
            
            print(f"{t_id:<5} | {name:<30} | {home_count} / {away_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    audit_teams()
