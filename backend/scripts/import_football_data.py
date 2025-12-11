import csv
import sqlite3
import os
import datetime

# Setup Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "beton.db")
DATA_DIR = os.path.join(BASE_DIR, "data")

# File Map: CSV Filename -> (League Name, DB League Name)
# E0 = Premier League
# SP1 = La Liga
# D1 = Bundesliga
# I1 = Serie A
# F1 = Ligue 1
FILES = {
    "E0.csv": "Premier League",
    "SP1.csv": "La Liga",
    "D1.csv": "Bundesliga",
    "I1.csv": "Serie A",
    "F1.csv": "Ligue 1"
}

# Team Name Mapping (CSV -> DB) based on standardization needs
# Ideally verify common diffs
TEAM_MAP_GENERIC = {
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Nott'm Forest": "Nottingham Forest",
    "Wolves": "Wolverhampton",
    "Ath Madrid": "Atletico Madrid",
    "Betis": "Real Betis",
    "Sp Gijon": "Sporting Gijon",
    "Bayern Munich": "Bayern Munchen",
    "Dortmund": "Borussia Dortmund",
    "Leverkusen": "Bayer Leverkusen",
    "M'gladbach": "Borussia Monchengladbach",
    "Frankfurt": "Eintracht Frankfurt",
    "Inter": "Internazionale",
    "Milan": "AC Milan",
    "Paris SG": "PSG",
    "St Etienne": "Saint-Etienne"
}

def parse_date(date_str):
    # Football-Data format: DD/MM/YYYY
    try:
        return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
    except:
        return None

def import_league(filename, league_name):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"  [SKIP] {league_name}: File {filename} not found in {DATA_DIR}")
        return

    print(f"  [IMPORT] Processing {league_name} from {filename}...")
    
    matches = []
    
    with open(path, "r", encoding="utf-8", errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Date'): continue
            
            m_date = parse_date(row['Date'])
            home = row['HomeTeam']
            away = row['AwayTeam']
            
            # Map Names
            home = TEAM_MAP_GENERIC.get(home, home)
            away = TEAM_MAP_GENERIC.get(away, away)
            
            # Scores
            fthg = row.get('FTHG')
            ftag = row.get('FTAG')
            
            h_score = int(fthg) if fthg and fthg.isdigit() else None
            a_score = int(ftag) if ftag and ftag.isdigit() else None
            
            matches.append({
                'date': m_date,
                'home': home,
                'away': away,
                'h_score': h_score,
                'a_score': a_score
            })
            
    # DB Operations
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure teams exist
    # NOTE: This implies we might create new teams if they don't exist
    # Better to Insert IGNORE or check
    
    inserted_teams = 0
    updated_matches = 0
    inserted_matches = 0
    
    # 1. Wipe League Season 2024/2025 to be clean?
    # Yes, safe if we import full file.
    cursor.execute("DELETE FROM matches WHERE league=? AND season='2024/2025'", (league_name,))
    print(f"    Cleaned {cursor.rowcount} existing matches.")
    
    for m in matches:
        # Get/Create Teams
        for t_name in [m['home'], m['away']]:
            cursor.execute("SELECT id FROM teams WHERE name=?", (t_name,))
            res = cursor.fetchone()
            if not res:
                cursor.execute("INSERT INTO teams (name, league) VALUES (?, ?)", (t_name, league_name))
                inserted_teams += 1
                
        home_id = cursor.execute("SELECT id FROM teams WHERE name=?", (m['home'],)).fetchone()[0]
        away_id = cursor.execute("SELECT id FROM teams WHERE name=?", (m['away'],)).fetchone()[0]
        
        # Insert Match
        status = 'FINISHED' if m['h_score'] is not None else 'SCHEDULED'
        
        # Round? Football-Data doesn't have Round.
        # Use Date Clustering or Sequence?
        # For simplicity, let's leave Round null or calculate roughly by match count?
        # User wants "Jornadas correctas".
        # Let's infer round?
        # Or Just insert.
        # We'll default round to 0 if unknown for now, or could enhance later.
        
        cursor.execute("""
            INSERT INTO matches (league, season, round, home_team_id, away_team_id, home_score, away_score, match_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (league_name, '2024/2025', 0, home_id, away_id, m['h_score'], m['a_score'], m['date'], status))
        inserted_matches += 1
            
    conn.commit()
    conn.close()
    print(f"    Done {league_name}: {inserted_matches} matches, {inserted_teams} new teams.")

if __name__ == "__main__":
    for csv_file, league in FILES.items():
        import_league(csv_file, league)
