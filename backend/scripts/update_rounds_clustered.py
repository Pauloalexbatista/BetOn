import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

def cluster_rounds():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
def cluster_rounds_for_league(league_name):
    print(f"\n--- Clustering {league_name} ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get matches
    cursor.execute("""
        SELECT id, match_date, home_team_id, away_team_id 
        FROM matches 
        WHERE season = '2024/2025' AND league = ?
        ORDER BY match_date
    """, (league_name,))
    
    matches = cursor.fetchall()
     
    if not matches:
        print("  No matches found.")
        conn.close()
        return

    print(f"  Matches: {len(matches)}")
    
    rounds_map = {} 
    current_round = 1
    
    # Initialize
    try:
        current_cluster_date = datetime.strptime(str(matches[0][1]).split()[0], "%Y-%m-%d")
    except:
        # If date format is YYYY-MM-DD from import
         current_cluster_date = datetime.strptime(str(matches[0][1]), "%Y-%m-%d")
         
    rounds_map[matches[0][0]] = current_round
    
    for i in range(1, len(matches)):
        m_id, m_date_str, home, away = matches[i]
        
        try:
            if " " in str(m_date_str):
                m_date = datetime.strptime(str(m_date_str).split()[0], "%Y-%m-%d")
            else:
                m_date = datetime.strptime(str(m_date_str), "%Y-%m-%d")
        except:
             continue
            
        gap = (m_date - current_cluster_date).days
        
        # Gap > 3 days triggers new round (Typical 4-5 days gap between weekends)
        if gap > 3:
            # print(f"    [Split] Gap {gap} days -> Round {current_round + 1}")
            current_round += 1
            
        rounds_map[m_id] = current_round
        current_cluster_date = m_date
        
    print(f"  Assigned {current_round} rounds.")
    
    # Batch Update
    for mid, r_num in rounds_map.items():
        cursor.execute("UPDATE matches SET round = ? WHERE id = ?", (str(r_num), mid))
        
    conn.commit()
    conn.close()

def cluster_all():
    leagues = ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
    for l in leagues:
        cluster_rounds_for_league(l)

if __name__ == "__main__":
    cluster_all()

if __name__ == "__main__":
    cluster_rounds()
