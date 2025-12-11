import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import time

# Database Path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beton.db")

# ZeroZero -> Database Name Mapping
# DB Names: Arouca, Benfica, Boavista, Casa Pia, Estoril, Estrela, Famalicao, Farense, 
# Gil Vicente, Guimaraes, Moreirense, Nacional, Portimonense, Porto, Rio Ave, 
# SC Braga, Santa Clara, Sporting, Vizela (and others if old seasons)
NAME_MAP = {
    "FC Porto": "Porto",
    "SL Benfica": "Benfica",
    "Sporting": "Sporting",
    "SC Braga": "SC Braga",
    "Vitória SC": "Guimaraes", # ZeroZero often uses Vitória SC
    "V. Guimarães": "Guimaraes",
    "FC Arouca": "Arouca",
    "FC Famalicão": "Famalicao",
    "Estoril Praia": "Estoril",
    "Casa Pia AC": "Casa Pia",
    "Boavista FC": "Boavista",
    "Gil Vicente FC": "Gil Vicente",
    "Moreirense FC": "Moreirense",
    "Rio Ave FC": "Rio Ave",
    "SC Farense": "Farense",
    "CF Estrela Amadora": "Estrela",
    "Estrela Amadora": "Estrela",
    "Est. Amadora": "Estrela",
    "CD Nacional": "Nacional",
    "CD Santa Clara": "Santa Clara",
    "CD Santa Clara": "Santa Clara",
    "AVS": "AVS", 
    "AFS": "AVS",
    "FC Alverca": "Alverca",
    "CD Tondela": "Tondela",
}

class ZeroZeroRoundUpdater:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _normalize_name(self, name):
        name = name.strip()
        return NAME_MAP.get(name, name)

    def _parse_date(self, date_text):
        """Parse date from DD/MM format. Assumes current season context."""
        try:
            # Format usually "DD/MM" or "DD/MM/YYYY" or plain text
            match = re.search(r'(\d{2})/(\d{2})', date_text)
            if match:
                day, month = int(match.group(1)), int(match.group(2))
                
                # Logic for season year crossing
                # Season starts ~August (08) -> Year X
                # Season ends ~May (05) -> Year X+1
                
                # We'll valid against current date to be safe or just standard logic
                # For 24/25 Season:
                year = 2024 if month >= 7 else 2025
                
                return f"{year}-{month:02d}-{day:02d}"
            return None
        except:
            return None

    def fetch_round(self, league_slug, round_num):
        url = f"https://www.zerozero.pt/competicao/{league_slug}?jornada_in={round_num}"
        print(f"  Fetching Round {round_num}: {url}")
        
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"    ❌ Failed to fetch: {resp.status_code}")
                return []
                
            soup = BeautifulSoup(resp.content, 'html.parser')
            soup = BeautifulSoup(resp.content, 'html.parser')
            tables = soup.find_all('table', class_='zztable')
            
            if not tables:
                print("    ❌ No 'zztable' found")
                return []
                
            matches = []
            
            for table in tables:
                rows = table.find_all('tr')[1:] # Skip header
            
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 3: continue
                    
                    # ZeroZero Table Columns (Jornada View):
                    # 0: Date/Time
                    # 1: Home Team (text-right)
                    # 2: Result (center)
                    # 3: Away Team (text-left)
                    # 4: TV/Obs
                    
                    # Check column count to be sure
                    # Sometimes structure is: Date | Status | Home | Result | Away
                    
                    # Let's try to extract based on link classes or alignment if standard fails
                    
                    # Attempt 1: Standard 
                    # Cell 0: Date
                    date_text = cells[0].get_text(" ", strip=True)
                    match_date = self._parse_date(date_text)
                    
                    home_team = None
                    away_team = None
                    home_score = None
                    away_score = None
                    
                    # Find all links to teams
                    links = row.find_all('a', href=True)
                    team_links = [l for l in links if '/equipa/' in l['href'] and not 'img' in str(l)]
                    
                    # Filter out "video" or other false positives if any
                    # Actually, zz often puts team names in b or simple text.
                    
                    # Robust approach: Get text from relevant cells
                    text_content = row.get_text(" | ", strip=True) # "Date | Home | Score | Away"
                    parts = text_content.split("|")
                    
                    # Use matches array to help debug
                    # print(f"Row: {text_content}")

                    if len(team_links) >= 2:
                        # Usually 0 is Home, 1 is Away
                        home_name_raw = team_links[0].get_text(strip=True)
                        away_name_raw = team_links[1].get_text(strip=True)
                        
                        # Sometimes logo links duplicate
                        # We can dedupe by text
                        
                        home_team = self._normalize_name(home_name_raw)
                        away_team = self._normalize_name(away_name_raw)

                        # Score
                        # usually in the middle cell or link
                        score_text = row.get_text()
                        score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                        if score_match:
                            home_score = int(score_match.group(1))
                            away_score = int(score_match.group(2))
                    
                    if home_team and away_team:
                        matches.append({
                            'round': round_num,
                            'date': match_date,
                            'home': home_team,
                            'away': away_team,
                            'home_score': home_score,
                            'away_score': away_score
                        })
                    
            print(f"    ✅ Parsed {len(matches)} matches from tables")
            
            # If no matches found in tables (or few?), try div structure
            if len(matches) < 5:
                print("    ⚠️ Few table matches, trying DIV structure...")
                div_matches = self._parse_div_structure(soup, round_num)
                matches.extend(div_matches)
                print(f"    ✅ Parsed {len(div_matches)} matches from DIVs")

            return matches
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return []

    def _parse_div_structure(self, soup, round_num):
        matches = []
        games = soup.find_all('li', class_='game')
        
        for game in games:
            # Structure: 
            # li > a > div.team (Home) .. div.team (Away) .. div.date
            
            teams = game.find_all('div', class_='team')
            if len(teams) < 2: continue
            
            # Extract Names (excluding child spans like 'Jun.A')
            # Home
            home_title_span = teams[0].find('span', class_='title')
            # Get text node only, ignoring children
            home_name_raw = home_title_span.find(text=True, recursive=False)
            if not home_name_raw: home_name_raw = home_title_span.get_text(strip=True) # Fallback
            
            # Away
            away_title_span = teams[1].find('span', class_='title')
            away_name_raw = away_title_span.find(text=True, recursive=False)
            if not away_name_raw: away_name_raw = away_title_span.get_text(strip=True)
            
            home_team = self._normalize_name(str(home_name_raw).strip())
            away_team = self._normalize_name(str(away_name_raw).strip())
            
            # Check if relevant teams (must be in our map/DB to allow update)
            # If "Bayern", it won't be mapped so effectively works if we had checking.
            # But relying on DB match later is safer.
            
            # Scores
            home_res = teams[0].find('span', class_='res')
            away_res = teams[1].find('span', class_='res')
            
            home_score = int(home_res.get_text(strip=True)) if home_res and home_res.get_text(strip=True).isdigit() else None
            away_score = int(away_res.get_text(strip=True)) if away_res and away_res.get_text(strip=True).isdigit() else None
            
            # Date
            date_div = game.find('div', class_='date')
            match_date = None
            if date_div:
                date_span = date_div.find('span')
                if date_span:
                    date_text = date_span.get_text(strip=True) # "09/12 - 12:30"
                    match_date = self._parse_date(date_text)
            
            matches.append({
                'round': round_num,
                'date': match_date,
                'home': home_team,
                'away': away_team,
                'home_score': home_score,
                'away_score': away_score
            })
            
        return matches

    def update_db(self, rounds):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total_updates = 0
        
        for r in rounds:
            matches = self.fetch_round("liga-portuguesa", r)
            time.sleep(1) # Be nice to content provider
            
            for m in matches:
                if not m['date']: continue
                
                # Update Query: Find match by Teams + Season (approx)
                # We assume current season matches (2024/2025)
                # We check for matches that might correspond
                
                # Note: Teams must match exactly our DB names.
                
                # Try finding valid match with retries
                for attempt in range(5):
                    try:
                        cursor.execute("""
                            SELECT id, round, match_date FROM matches 
                            WHERE home_team_id = (SELECT id FROM teams WHERE name = ?)
                            AND away_team_id = (SELECT id FROM teams WHERE name = ?)
                            AND (season LIKE '%2025%' OR season LIKE '2024/2025')
                        """, (m['home'], m['away']))
                        
                        db_match = cursor.fetchone()
                        
                        if db_match:
                            match_id, old_round, old_date = db_match
                            
                            # Only update if round missing or different, or date different
                            if str(old_round) != str(m['round']) or str(old_date).split()[0] != m['date']:
                                cursor.execute("""
                                    UPDATE matches SET round = ?, match_date = ? 
                                    WHERE id = ?
                                """, (m['round'], m['date'], match_id))
                                total_updates += 1
                        else:
                            # Debug unmatched to improve mapping
                            print(f"      ⚠️ No DB match for: {m['home']} vs {m['away']} (Looking in season 2025/2026)")
                        
                        break # Success
                    except sqlite3.OperationalError as e:
                        if "locked" in str(e):
                            print(f"      🔒 Database locked, retrying {attempt+1}/5...")
                            time.sleep(1)
                        else:
                            raise e

        conn.commit()
        conn.close()
        print(f"\nTotal Matches Updated: {total_updates}")

if __name__ == "__main__":
    updater = ZeroZeroRoundUpdater(DB_PATH)
    # Update rounds 1 to 14 (current season progress)
    updater.update_db(range(1, 15))
