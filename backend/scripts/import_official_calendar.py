import re
import sqlite3
import os
from datetime import datetime

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "beton.db")
# Path to TXT file (Raw Copy-Paste)
TXT_PATH = os.path.join(os.path.dirname(__file__), "official_calendar_2025.txt")

# Team Mapping (User Text -> DB Name)
TEAM_MAP = {
    "FC Porto": "Porto",
    "Porto": "Porto",
    "Sporting CP": "Sporting",
    "Sporting": "Sporting",
    "SL Benfica": "Benfica",
    "Benfica": "Benfica",
    "SC Braga": "SC Braga",
    "Sp. Braga": "SC Braga",
    "Braga": "SC Braga",
    "Vitória SC": "Guimaraes",
    "Vitória Guimarães": "Guimaraes",
    "FC Famalicão": "Famalicao",
    "Famalicão": "Famalicao",
    "Estrela da Amadora": "Estrela",
    "Estrela Amadora": "Estrela",
    "FC Alverca": "Alverca",
    "Alverca": "Alverca",
    "FC Arouca": "Arouca",
    "Arouca": "Arouca",
    "CD Nacional": "Nacional",
    "Nacional": "Nacional",
    "AVS SAD": "AVS",
    "AVS": "AVS",
    "Aves SAD": "AVS",
    "CD Tondela": "Tondela",
    "Tondela": "Tondela",
    "Casa Pia": "Casa Pia", 
    "Moreirense": "Moreirense",
    "Gil Vicente": "Gil Vicente",
    "Rio Ave": "Rio Ave",
    "Estoril": "Estoril",
    "Estoril Praia": "Estoril",
    "Santa Clara": "Santa Clara",
    "CD Santa Clara": "Santa Clara",
    "Boavista": "Boavista",
    "Boavista FC": "Boavista",
    "Farense": "Farense",
    "SC Farense": "Farense"
}

def import_calendar():
    if not os.path.exists(TXT_PATH):
        print(f"File not found: {TXT_PATH}")
        return

    with open(TXT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    matches_to_insert = []
    current_round = None
    
    print("--- Parsing RAW TXT Calendar ---")
    
    # Regex for "Home Score-Score Away" e.g. "FC Porto 3-0 Gil Vicente"
    # Also handles "Home vs Away" for future matches
    score_pattern = re.compile(r"^(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)$")
    future_pattern = re.compile(r"^(.+?)\s+vs\s+(.+)$")
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Detect Round Header
        # "Jornada 1 (9-12 Agosto) | ✅ Realizada"
        # "Jornada 14 (13-15 Dezembro)"
        if line.startswith("Jornada"):
            try:
                # Extract number
                parts = line.split()
                current_round = int(parts[1])
                print(f"Processing Round {current_round}...")
            except:
                print(f"Error parsing header: {line}")
            continue
            
        if not current_round: continue
        
        # Skip unrelated lines
        if "VOLTA" in line: continue
        
        # Parse Match Line
        home = None
        away = None
        h_score = None
        a_score = None
        
        # Try Score Pattern (Finished Matches)
        m = score_pattern.match(line)
        if m:
            home_raw = m.group(1).strip()
            h_score = int(m.group(2))
            a_score = int(m.group(3))
            away_raw = m.group(4).strip()
        else:
            # Try Future Pattern
            m_fut = future_pattern.match(line)
            if m_fut:
                home_raw = m_fut.group(1).strip()
                away_raw = m_fut.group(2).strip()
            else:
                # Maybe just noise or unknown format
                continue
        
        # Normalize Names
        home = TEAM_MAP.get(home_raw)
        away = TEAM_MAP.get(away_raw)
        
        # DEBUG PRINT
        if current_round == 1:
            print(f"DEBUG: Line='{line.strip()}' -> Raw='{home_raw}'/'{away_raw}' -> Map='{home}'/'{away}'")
        
        if not home or not away:
             print(f"  UNKNOWN TEAMS: '{home_raw}' / '{away_raw}'")
             continue
             
        # Date is tricky in TXT (it's in header range). 
        # We'll set a default "Sunday" date or leave parsing for later enhancement.
        # For now, simplistic date: 2024-08-01 + (Round * 7 days).
        # OR better: The script already finds existing matches to update, so date isn't CRITICAL for update.
        # But for INSERT, we need a date.
        # Let's ESTIMATE date based on Round to avoid NULL errors.
        # Season start Aug 11 2024.
        # Match Date = 2024-08-11 + (Round-1)*7
        from datetime import timedelta, date
        base_date = date(2024, 8, 11)
        est_date = base_date + timedelta(weeks=current_round-1)
        
        matches_to_insert.append({
            'round': current_round,
            'date': est_date,
            'home': home,
            'away': away,
            'home_score': h_score,
            'away_score': a_score
        })

    # --- MIRROR LOGIC FILL (J18-J34) ---
    print("--- Filling Gaps with Mirror Logic ---")
    
    # Map [Round][Home_ID] -> Match (to check existence)
    # But names are strings here.
    matches_by_round = {}
    for m in matches_to_insert:
        r = m['round']
        if r not in matches_by_round: matches_by_round[r] = []
        matches_by_round[r].append(m)
        
    # Helper to check if match exists in round r
    def match_exists(r, team_a, team_b):
        if r not in matches_by_round: return False
        for m in matches_by_round[r]:
            # Check if this matchup exists (Home=A, Away=B)
            if m['home'] == team_a and m['away'] == team_b:
                return True
        return False

    for r in range(18, 35):
        source_round = r - 17
        if source_round not in matches_by_round:
            print(f"  Warning: Source R{source_round} missing for R{r}")
            continue
            
        source_matches = matches_by_round[source_round]
        
        for sm in source_matches:
            # Expected Mirror: Home = sm.Away, Away = sm.Home
            expected_home = sm['away']
            expected_away = sm['home']
            
            # Check coverage
            if not match_exists(r, expected_home, expected_away):
                 print(f"  Inferred R{r}: {expected_home} vs {expected_away} (Mirror R{source_round})")
                 # Date? Use existing R{r} matches date or dummy
                 # Try to find a date from existing matches in this round
                 inferred_date = None
                 if r in matches_by_round and matches_by_round[r]:
                     inferred_date = matches_by_round[r][0]['date'] # borrow date
                     
                 new_match = {
                    'round': r,
                    'date': inferred_date,
                    'home': expected_home,
                    'away': expected_away,
                    'home_score': None,
                    'away_score': None
                 }
                 matches_to_insert.append(new_match)
                 if r not in matches_by_round: matches_by_round[r] = []
                 matches_by_round[r].append(new_match)

    print(f"Total Matches after Fill: {len(matches_to_insert)}")
    
    # DEBUG: Check for Sporting match
    found_sporting = False
    for m in matches_to_insert:
        if m['home'] == 'Sporting' and m['away'] == 'Rio Ave':
            print(f"DEBUG: FOUND Sporting vs Rio Ave in list! Round={m['round']}, Date={m['date']}")
            found_sporting = True
            break
    if not found_sporting:
        print("DEBUG: CRITICAL! Sporting vs Rio Ave NOT in insert list!")
    
    print(f"Connecting to DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Debug Leagues
    cursor.execute("SELECT distinct league FROM matches WHERE season='2025/2026'")
    leagues = cursor.fetchall()
    print(f"Leagues in 2025/2026 (BAD DATA) before wipe: {leagues}")
    
    # WIPE ALL related to 2025 (2024/2025, 2025/2026, etc)
    print("--- Cleaning Season 2024/2025 (Clean Slate) ---")
    cursor.execute("DELETE FROM matches WHERE season LIKE '%2025%' OR season LIKE '2024/2025'")
    print(f"Deleted {cursor.rowcount} matches from 2025 seasons.")
    
    conn.commit()
    
    # Debug schema
    cursor.execute("PRAGMA table_info(matches)")
    cols = [info[1] for info in cursor.fetchall()]
    print(f"Match Table Columns: {cols}")
    
    if "round" not in cols:
        print("CRITICAL: 'round' column missing!")
        return
    
    # Ensure teams exist
    print("--- Verifying Teams ---")
    cursor.execute("SELECT name FROM teams")
    existing_team_names = {row[0] for row in cursor.fetchall()}
    
    # Check all teams in matches_to_insert
    teams_needed = set()
    for m in matches_to_insert:
        if m['home']: teams_needed.add(m['home'])
        if m['away']: teams_needed.add(m['away'])
        
    for t_name in teams_needed:
        if t_name not in existing_team_names:
            print(f"Creating missing team: {t_name}")
            cursor.execute("INSERT INTO teams (name, league) VALUES (?, ?)", (t_name, 'Primeira Liga'))
            existing_team_names.add(t_name)
            
    conn.commit()

    # Re-fetch IDs map
    cursor.execute("SELECT name, id FROM teams")
    db_teams = {row[0]: row[1] for row in cursor.fetchall()}
    
    updated = 0
    inserted = 0
    
    for m in matches_to_insert:
        home_id = db_teams.get(m['home'])
        away_id = db_teams.get(m['away'])
        
        # DEBUG SPECIFIC MATCH
        if m['home'] == 'Sporting' and m['away'] == 'Rio Ave':
            print(f"DEBUG INSERTION: Sporting vs Rio Ave -> Round {m['round']} (Should be 1)")
        
        if not home_id or not away_id:
            print(f"Skipping match, ID not found: {m['home']} vs {m['away']}")
            continue
            
        # Upsert Logic
        # Try finding by home/away/season
        cursor.execute("""
            SELECT id FROM matches 
            WHERE home_team_id = ? AND away_team_id = ? AND season = '2024/2025'
        """, (home_id, away_id))
        row = cursor.fetchone()
        
        status = 'finished' if m['home_score'] is not None else 'SCHEDULED'
        
        if row:
            # Update
            mid = row[0]
            
            # PROTECT FINISHED MATCHES from being overwritten by duplicates/ghosts
            # If DB match is FINISHED and new match is SCHEDULED, skip!
            cursor.execute("SELECT status FROM matches WHERE id=?", (mid,))
            current_status = cursor.fetchone()[0]
            
            if current_status == 'finished' and status == 'SCHEDULED':
                print(f"Skipping overwrite of FINISHED match {mid} (R {m['round']}) with SCHEDULED data.")
                continue

            cursor.execute("""
                UPDATE matches 
                SET round = ?, 
                    home_score = COALESCE(?, home_score), 
                    away_score = COALESCE(?, away_score),
                    status = ?,
                    league = ?,
                    season = ?
                WHERE id = ?
            """, (m['round'], m['home_score'], m['away_score'], status, 'Primeira Liga', '2024/2025', mid))
            updated += 1
        else:
            # Insert
            # We need a date. COALESCE with "2025-01-01" fallback
            final_date = m['date'] if m['date'] else f"2025-01-01" 
            
            cursor.execute("""
                INSERT INTO matches (league, season, round, home_team_id, away_team_id, home_score, away_score, match_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ('Primeira Liga', '2024/2025', m['round'], home_id, away_id, m['home_score'], m['away_score'], final_date, status))
            inserted += 1
            
    conn.commit()
    conn.close()
    print(f"Done. Updated: {updated}, Inserted: {inserted}")

if __name__ == "__main__":
    import_calendar()
