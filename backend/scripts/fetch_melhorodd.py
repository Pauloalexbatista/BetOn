"""
MelhorOdd.pt Collector
Scrapes Liga Portugal fixtures and odds
"""
import sys
sys.path.insert(0, '/app')

import requests
from bs4 import BeautifulSoup
from database.database import SessionLocal
from database.models import Match, Team, Odds
from datetime import datetime
import re

def get_or_create_team(db, name: str):
    """Get or create team"""
    team = db.query(Team).filter(Team.name == name).first()
    if not team:
        team = Team(name=name, league="Primeira Liga", country="Portugal")
        db.add(team)
        db.flush()
    return team

def parse_date(date_str: str) -> datetime:
    """Parse Portuguese date format"""
    # Formato: "13 dez" ou "13 dez 2024"
    months = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }
    
    parts = date_str.lower().strip().split()
    day = int(parts[0])
    month = months.get(parts[1], 12)
    year = int(parts[2]) if len(parts) > 2 else 2024
    
    # Se é dezembro e estamos em dezembro/2024, é 2024
    # Se é janeiro-junho, provavelmente é 2025
    if month <= 6:
        year = 2025
    
    return datetime(year, month, day)

def main():
    db = SessionLocal()
    
    try:
        print("🔍 Fetching from MelhorOdd.pt...")
        print("=" * 60)
        
        url = "https://www.melhorodd.pt/primeira-liga/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find matches
        matches_found = 0
        created = 0
        updated = 0
        
        # Find all match containers (structure may vary)
        match_divs = soup.find_all('div', class_='match') or soup.find_all('tr', class_='match-row')
        
        if not match_divs:
            # Try alternative selectors
            match_divs = soup.find_all('div', {'data-match-id': True})
        
        print(f"Found {len(match_divs)} match containers")
        
        for match_div in match_divs:
            try:
                # Extract teams (adapt based on actual HTML)
                home = match_div.find(class_='team-home') or match_div.find(class_='home')
                away = match_div.find(class_='team-away') or match_div.find(class_='away')
                
                if not home or not away:
                    continue
                
                home_name = home.get_text(strip=True)
                away_name = away.get_text(strip=True)
                
                # Extract date
                date_elem = match_div.find(class_='date') or match_div.find(class_='match-date')
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                    match_date = parse_date(date_str)
                else:
                    match_date = datetime.now()
                
                # Extract odds (1X2)
                odds_home = None
                odds_draw = None
                odds_away = None
                
                odds_divs = match_div.find_all(class_='odd') or match_div.find_all(class_='odds')
                if len(odds_divs) >= 3:
                    try:
                        odds_home = float(odds_divs[0].get_text(strip=True))
                        odds_draw = float(odds_divs[1].get_text(strip=True))
                        odds_away = float(odds_divs[2].get_text(strip=True))
                    except:
                        pass
                
                # Get teams
                home_team = get_or_create_team(db, home_name)
                away_team = get_or_create_team(db, away_name)
                
                # Check existing
                existing = db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.season == "2024/2025"
                ).first()
                
                if existing:
                    existing.match_date = match_date
                    existing.status = 'scheduled'
                    updated += 1
                else:
                    new_match = Match(
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        league="Primeira Liga",
                        season="2024/2025",
                        match_date=match_date,
                        status='scheduled'
                    )
                    db.add(new_match)
                    db.flush()
                    created += 1
                    
                    # Add odds if available
                    if odds_home and odds_draw and odds_away:
                        odds = Odds(
                            match_id=new_match.id,
                            bookmaker="Betano",
                            market="1X2",
                            home_odds=odds_home,
                            draw_odds=odds_draw,
                            away_odds=odds_away
                        )
                        db.add(odds)
                
                matches_found += 1
                print(f"  ✅ {home_name} vs {away_name} ({match_date.strftime('%Y-%m-%d')})")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"📊 Results:")
        print(f"   Found: {matches_found}")
        print(f"   Created: {created}")
        print(f"   Updated: {updated}")
        
        # Verify
        total_scheduled = db.query(Match).filter(
            Match.season == "2024/2025",
            Match.status == "scheduled"
        ).count()
        
        print(f"\n✅ Total scheduled 2024/2025: {total_scheduled}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
