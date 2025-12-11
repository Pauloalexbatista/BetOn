"""
Update Match Rounds from ZeroZero - Simplified Version
Uses direct SQLite connection
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class SimpleZeroZeroUpdater:
    """Simplified updater using direct SQLite"""
    
    def __init__(self, db_path='beton.db'):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_round_matches(self, league: str, round_num: int):
        """Fetch matches for a specific round"""
        url = f"https://www.zerozero.pt/competicao/{league}?jornada_in={round_num}"
        
        try:
            print(f"  Fetching round {round_num}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            
            # Find all match rows in the table
            match_table = soup.find('table', class_='zztable')
            if not match_table:
                print(f"    ⚠️  No match table found")
                return matches
            
            rows = match_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Extract date
                    date_text = cells[0].get_text(strip=True)
                    match_date = self._parse_date(date_text)
                    
                    # Extract teams and score
                    match_cell = cells[1]
                    match_text = match_cell.get_text(strip=True)
                    
                    # Parse "Team1 X-Y Team2" format
                    parts = match_text.split()
                    if len(parts) >= 3:
                        # Find score pattern
                        score_idx = None
                        for i, part in enumerate(parts):
                            if '-' in part and any(c.isdigit() for c in part):
                                score_idx = i
                                break
                        
                        if score_idx:
                            home_team = ' '.join(parts[:score_idx])
                            away_team = ' '.join(parts[score_idx+1:])
                            score = parts[score_idx]
                            
                            score_match = re.match(r'(\d+)-(\d+)', score)
                            if score_match:
                                home_score = int(score_match.group(1))
                                away_score = int(score_match.group(2))
                                
                                matches.append({
                                    'round': round_num,
                                    'date': match_date,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'home_score': home_score,
                                    'away_score': away_score
                                })
            
            print(f"    ✅ Found {len(matches)} matches")
            return matches
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return []
    
    def _parse_date(self, date_text: str):
        """Parse date from DD/MM format"""
        try:
            if re.match(r'\d{2}/\d{2}', date_text):
                day, month = date_text.split('/')
                year = datetime.now().year
                if int(month) < 7 and datetime.now().month >= 7:
                    year += 1
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return None
        except:
            return None
    
    def update_database(self, rounds_to_update=range(1, 35)):
        """Update database with rounds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("🔄 Updating Liga Portuguesa Rounds")
        print("=" * 70)
        
        updated = 0
        
        for round_num in rounds_to_update:
            matches = self.fetch_round_matches("liga-portuguesa", round_num)
            
            for match in matches:
                # Find match by teams
                cursor.execute("""
                    SELECT m.id, m.round, m.match_date 
                    FROM matches m
                    JOIN teams ht ON m.home_team_id = ht.id
                    JOIN teams at ON m.away_team_id = at.id
                    WHERE ht.name = ? AND at.name = ?
                    AND m.league = 'Primeira Liga'
                    AND m.season LIKE '2024%'
                """, (match['home_team'], match['away_team']))
                
                result = cursor.fetchone()
                
                if result:
                    match_id, old_round, old_date = result
                    
                    # Update round and date
                    cursor.execute("""
                        UPDATE matches 
                        SET round = ?, match_date = ?, home_score = ?, away_score = ?, status = 'finished'
                        WHERE id = ?
                    """, (round_num, match['date'], match['home_score'], match['away_score'], match_id))
                    
                    if old_round != round_num:
                        print(f"    ✏️  {match['home_team']} vs {match['away_team']}: Round {old_round} → {round_num}")
                    
                    updated += 1
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 70)
        print(f"✅ Updated {updated} matches")
        print("=" * 70)


if __name__ == "__main__":
    updater = SimpleZeroZeroUpdater()
    
    # Update rounds 1-15 (adjust as needed)
    updater.update_database(rounds_to_update=range(1, 16))
