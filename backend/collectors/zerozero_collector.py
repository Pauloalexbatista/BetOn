"""
ZeroZero.pt Collector
Scrapes match data including seasons, rounds, dates, and results
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import re
from sqlalchemy.orm import Session

from database.models import Match, Team
from database.database import get_db


class ZeroZeroCollector:
    """
    Collector for ZeroZero.pt football data
    Extracts match schedules, rounds, and results
    """
    
    BASE_URL = "https://www.zerozero.pt"
    
    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_league_rounds(self, league: str = "liga-portuguesa", season: str = None) -> List[Dict]:
        """
        Fetch all rounds/jornadas for a league
        
        Args:
            league: League identifier (e.g., 'liga-portuguesa')
            season: Season (e.g., '2024/2025'), if None uses current
        
        Returns:
            List of round data with matches
        """
        url = f"{self.BASE_URL}/competicao/{league}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract season info
            season_info = self._extract_season(soup)
            if not season:
                season = season_info
            
            # Extract all rounds
            rounds_data = []
            
            # Find round selector
            round_selector = soup.find('select', {'name': 'jornada_in'})
            if round_selector:
                rounds = round_selector.find_all('option')
                
                for round_option in rounds:
                    round_num = round_option.get('value')
                    if round_num and round_num.isdigit():
                        print(f"Fetching round {round_num}...")
                        round_data = self.fetch_round_matches(league, int(round_num))
                        if round_data:
                            rounds_data.append({
                                'round': int(round_num),
                                'season': season,
                                'matches': round_data
                            })
            
            return rounds_data
            
        except Exception as e:
            print(f"Error fetching league rounds: {e}")
            return []
    
    def fetch_round_matches(self, league: str, round_num: int) -> List[Dict]:
        """
        Fetch matches for a specific round
        
        Args:
            league: League identifier
            round_num: Round/jornada number
        
        Returns:
            List of match data
        """
        url = f"{self.BASE_URL}/competicao/{league}?jornada_in={round_num}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            
            # Find match containers
            match_rows = soup.find_all('div', class_='match')
            if not match_rows:
                # Try alternative structure
                match_rows = soup.find_all('tr', class_='match-row')
            
            for match_row in match_rows:
                match_data = self._parse_match_row(match_row, round_num)
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            print(f"Error fetching round {round_num}: {e}")
            return []
    
    def _parse_match_row(self, row, round_num: int) -> Optional[Dict]:
        """Parse a single match row"""
        try:
            # Extract date
            date_elem = row.find('div', class_='date') or row.find('td', class_='date')
            match_date = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                match_date = self._parse_date(date_text)
            
            # Extract teams
            home_team_elem = row.find('div', class_='home-team') or row.find('td', class_='home')
            away_team_elem = row.find('div', class_='away-team') or row.find('td', class_='away')
            
            if not home_team_elem or not away_team_elem:
                return None
            
            home_team = home_team_elem.get_text(strip=True)
            away_team = away_team_elem.get_text(strip=True)
            
            # Extract score
            score_elem = row.find('div', class_='score') or row.find('td', class_='score')
            home_score = None
            away_score = None
            status = 'scheduled'
            
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                score_match = re.match(r'(\d+)-(\d+)', score_text)
                if score_match:
                    home_score = int(score_match.group(1))
                    away_score = int(score_match.group(2))
                    status = 'finished'
            
            return {
                'round': round_num,
                'date': match_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': status
            }
            
        except Exception as e:
            print(f"Error parsing match row: {e}")
            return None
    
    def _extract_season(self, soup) -> str:
        """Extract season from page"""
        # Look for season selector or title
        season_elem = soup.find('select', {'name': 'epoca'})
        if season_elem:
            selected = season_elem.find('option', {'selected': True})
            if selected:
                return selected.get_text(strip=True)
        
        # Try to find in title
        title = soup.find('h1')
        if title:
            season_match = re.search(r'(\d{4}/\d{4})', title.get_text())
            if season_match:
                return season_match.group(1)
        
        # Default to current season
        current_year = datetime.now().year
        if datetime.now().month >= 7:
            return f"{current_year}/{current_year + 1}"
        else:
            return f"{current_year - 1}/{current_year}"
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats"""
        try:
            # Format: "05/12" or "06/12"
            if re.match(r'\d{2}/\d{2}', date_text):
                day, month = date_text.split('/')
                year = datetime.now().year
                # Adjust year if month is in the past
                if int(month) < 7 and datetime.now().month >= 7:
                    year += 1
                return datetime(year, int(month), int(day))
            
            # Format: "05/12/2024"
            if re.match(r'\d{2}/\d{2}/\d{4}', date_text):
                day, month, year = date_text.split('/')
                return datetime(int(year), int(month), int(day))
            
            return None
            
        except Exception as e:
            print(f"Error parsing date '{date_text}': {e}")
            return None
    
    def update_database(self, rounds_data: List[Dict], league: str = "Primeira Liga"):
        """
        Update database with scraped data
        
        Args:
            rounds_data: List of round data from fetch_league_rounds()
            league: League name for database
        """
        updated = 0
        created = 0
        
        for round_info in rounds_data:
            round_num = round_info['round']
            season = round_info['season']
            
            for match_data in round_info['matches']:
                # Get or create teams
                home_team = self._get_or_create_team(match_data['home_team'])
                away_team = self._get_or_create_team(match_data['away_team'])
                
                # Find existing match
                existing = self.db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.league == league,
                    Match.season == season
                ).first()
                
                if existing:
                    # Update existing match
                    existing.round = round_num
                    if match_data['date']:
                        existing.match_date = match_data['date']
                    if match_data['home_score'] is not None:
                        existing.home_score = match_data['home_score']
                        existing.away_score = match_data['away_score']
                        existing.status = 'finished'
                    updated += 1
                else:
                    # Create new match
                    new_match = Match(
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        league=league,
                        season=season,
                        round=round_num,
                        match_date=match_data['date'],
                        home_score=match_data['home_score'],
                        away_score=match_data['away_score'],
                        status=match_data['status']
                    )
                    self.db.add(new_match)
                    created += 1
        
        self.db.commit()
        print(f"✅ Database updated: {created} created, {updated} updated")
    
    def _get_or_create_team(self, team_name: str) -> Team:
        """Get or create team by name"""
        team = self.db.query(Team).filter(Team.name == team_name).first()
        if not team:
            team = Team(name=team_name)
            self.db.add(team)
            self.db.flush()
        return team


def main():
    """Example usage"""
    db = next(get_db())
    collector = ZeroZeroCollector(db)
    
    print("🔍 Fetching Liga Portuguesa data from ZeroZero.pt...")
    
    # Fetch all rounds
    rounds_data = collector.fetch_league_rounds("liga-portuguesa")
    
    print(f"\n📊 Found {len(rounds_data)} rounds")
    
    # Update database
    if rounds_data:
        print("\n💾 Updating database...")
        collector.update_database(rounds_data, "Primeira Liga")
        print("✅ Done!")
    
    db.close()


if __name__ == "__main__":
    main()
