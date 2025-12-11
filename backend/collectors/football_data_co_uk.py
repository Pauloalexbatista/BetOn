
import logging
import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Team, Match, Odds
from config import get_settings

logger = logging.getLogger(__name__)

class FootballDataCoUkCollector:
    """
    Collector for football-data.co.uk CSV files.
    """
    
    BASE_URL = "https://www.football-data.co.uk/mmz4281"
    
    LEAGUES = {
        "P1": "Primeira Liga",
        "E0": "Premier League",
        "SP1": "La Liga",
        "I1": "Serie A",
        "D1": "Bundesliga",
        "F1": "Ligue 1"
    }
    
    # Team name normalization (English → Portuguese)
    TEAM_NAME_MAP = {
        # Sporting variations
        "Sp Lisbon": "Sporting",
        "Sporting Clube de Portugal": "Sporting",
        "Sporting CP": "Sporting",
        
        # Benfica variations
        "Sport Lisboa e Benfica": "Benfica",
        "SL Benfica": "Benfica",
        
        # Porto variations
        "FC Porto": "Porto",
        
        # Braga variations
        "Sp Braga": "SC Braga",
        "Sporting Clube de Braga": "SC Braga",
        "Sporting Braga": "SC Braga",

        # New Consolidations (Approved 2025-12-10)
        "FC Arouca": "Arouca",
        "GD Estoril Praia": "Estoril",
        "CF Estrela da Amadora": "Estrela",
        "FC Famalicão": "Famalicao",
        "FC FamalicÒo": "Famalicao",
        "SC Farense": "Farense",
        "Vitória Guimarães": "Guimaraes",
        "Vit¾ria GuimarÒes": "Guimaraes",
        "CD Nacional": "Nacional",
        "CD Santa Clara": "Santa Clara",
        "Casa Pia AC": "Casa Pia",
    }

    def __init__(self, db: Session = None):
        self.db = db if db else SessionLocal()
        
    def sync_history(self, years: int = 3):
        """
        Sync data for all configured leagues for the last N years.
        years=3 means: Current season + 2 previous.
        """
        # Calculate seasons
        # Current is 2526 (Dec 2025)
        # We want 2526, 2425, 2324
        
        # Taking "26" as end of current season
        current_end_year = 26 
        
        seasons = []
        for i in range(years):
            end = current_end_year - i
            start = end - 1
            code = f"{start:02d}{end:02d}" # "2526"
            seasons.append(code)
            
        logger.info(f"Syncing History for {years} years: {seasons}")
        logger.info(f"Target Leagues: {list(self.LEAGUES.keys())}")
        
        for league_code in self.LEAGUES.keys():
            for season in seasons:
                self.sync_season(league_code, season)

    def sync_season(self, league_code: str, season_code: str):
        """
        Download and sync data for a specific league and season.
        """
        if league_code not in self.LEAGUES:
            logger.error(f"Unknown league code: {league_code}")
            return

        url = f"{self.BASE_URL}/{season_code}/{league_code}.csv"
        logger.info(f"Downloading [{self.LEAGUES[league_code]}] {season_code} from: {url}")
        
        try:
            # Read CSV directly into pandas DataFrame
            # On bad URLs (future seasons not yet started, or errors), pandas usually raises HTTPError
            df = pd.read_csv(url)
            logger.info(f"Downloaded {len(df)} rows.")
            
            # Process Data
            self._process_data(df, league_code, season_code)
            
        except Exception as e:
            # It's common for current season to have moved or simple error if 404
            logger.warning(f"Could not download/process {league_code} {season_code}: {e}")

    def _process_data(self, df: pd.DataFrame, league_code: str, season_code: str):
        """Process DataFrame and save to DB"""
        
        league_name = self.LEAGUES[league_code]
        
        # Clean data (remove empty rows if any)
        df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
        
        # Determine season string (e.g. "2025/2026")
        start_year = "20" + season_code[:2]
        end_year = "20" + season_code[2:]
        season_str = f"{start_year}/{end_year}"

        count_new = 0
        count_updated = 0
        
        for _, row in df.iterrows():
            try:
                # 1. Sync Teams (Pass match info to help distinguish if needed later)
                home_team = self._get_or_create_team(row['HomeTeam'], row.get('Country', None) or league_name)
                away_team = self._get_or_create_team(row['AwayTeam'], row.get('Country', None) or league_name)
                
                # 2. Parse Date
                date_str = row['Date']
                try:
                    # football-data.co.uk mixes formats: dd/mm/yy (classic) and dd/mm/yyyy
                    match_date = pd.to_datetime(date_str, dayfirst=True).to_pydatetime()
                except:
                    logger.warning(f"Could not parse date: {date_str}")
                    continue

                # 3. Find or Create Match
                match = self.db.query(Match).filter(
                    Match.home_team_id == home_team.id,
                    Match.away_team_id == away_team.id,
                    Match.match_date == match_date
                ).first()
                
                if match:
                    self._update_match_stats(match, row)
                    count_updated += 1
                else:
                    match = self._create_match(home_team, away_team, match_date, season_str, league_name, row)
                    count_new += 1
                
                # 4. Sync Odds
                self._sync_odds(match, row)
                
            except Exception as e:
                logger.error(f"Error processing row: {row.get('HomeTeam', 'Unknown')} vs {row.get('AwayTeam', 'Unknown')} - {e}")
                continue
                
        self.db.commit()
        logger.info(f"[{league_name} {season_code}] Sync Complete. New: {count_new}, Updated: {count_updated}")

    def _get_or_create_team(self, team_name: str, context: str) -> Team:
        # Normalize team name first
        name = team_name.strip()
        name = self.TEAM_NAME_MAP.get(name, name)  # Apply mapping if exists
        
        # Basic caching/checking
        team = self.db.query(Team).filter(Team.name == name).first()
        
        if not team:
            # Generate ID
            temp_id = abs(hash(name)) % 100000000
            while self.db.query(Team).filter(Team.api_id == temp_id).first():
                temp_id += 1
            
            # Context usually maps to country/league roughly
            country = "Unknown"
            if "Primeira" in context: country = "Portugal"
            elif "Premier" in context: country = "England"
            elif "La Liga" in context: country = "Spain"
            elif "Serie A" in context: country = "Italy"
            elif "Bundesliga" in context: country = "Germany"
            elif "Ligue 1" in context: country = "France"
            
            team = Team(
                name=name,
                api_id=temp_id, 
                country=country,
                league=context 
            )
            self.db.add(team)
            self.db.flush()
            
        return team

    def _create_match(self, home_team, away_team, match_date, season, league_name, row):
        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=match_date,
            season=season,
            league=league_name,
            status="finished" if pd.notna(row.get('FTHG')) else "scheduled",
            
            # Scores
            home_score=int(row['FTHG']) if pd.notna(row.get('FTHG')) else None,
            away_score=int(row['FTAG']) if pd.notna(row.get('FTAG')) else None,
            
            # Stats
            home_shots=self._get_int(row, 'HS'),
            away_shots=self._get_int(row, 'AS'),
            home_shots_target=self._get_int(row, 'HST'),
            away_shots_target=self._get_int(row, 'AST'),
            home_corners=self._get_int(row, 'HC'),
            away_corners=self._get_int(row, 'AC'),
            home_fouls=self._get_int(row, 'HF'),
            away_fouls=self._get_int(row, 'AF'),
            home_yellow=self._get_int(row, 'HY'),
            away_yellow=self._get_int(row, 'AY'),
            home_red=self._get_int(row, 'HR'),
            away_red=self._get_int(row, 'AR'),
            referee=row.get('Referee', None)
        )
        self.db.add(match)
        self.db.flush()
        return match

    def _update_match_stats(self, match, row):
        # Update scores and stats if available
        if pd.notna(row.get('FTHG')):
            match.home_score = int(row['FTHG'])
            match.away_score = int(row['FTAG'])
            match.status = "finished"
        
        match.home_shots = self._get_int(row, 'HS')
        match.away_shots = self._get_int(row, 'AS')
        match.home_shots_target = self._get_int(row, 'HST')
        match.away_shots_target = self._get_int(row, 'AST')
        match.home_corners = self._get_int(row, 'HC')
        match.away_corners = self._get_int(row, 'AC')
        match.home_fouls = self._get_int(row, 'HF')
        match.away_fouls = self._get_int(row, 'AF')
        match.home_yellow = self._get_int(row, 'HY')
        match.away_yellow = self._get_int(row, 'AY')
        match.home_red = self._get_int(row, 'HR')
        match.away_red = self._get_int(row, 'AR')
        match.referee = row.get('Referee')

    def _sync_odds(self, match, row):
        # Import Average and Max odds if available (AvgH, AvgD, AvgA, MaxH, MaxD, MaxA)
        # Also Bet365 (B365H, B365D, B365A)
        
        odds_sources = [
            ("Avg", "AvgH", "AvgD", "AvgA"),
            ("Max", "MaxH", "MaxD", "MaxA"),
            ("Bet365", "B365H", "B365D", "B365A"),
            ("Pinnacle", "PSH", "PSD", "PSA")
        ]
        
        for name, col_h, col_d, col_a in odds_sources:
            if pd.isna(row.get(col_h)):
                continue
                
            odds_data = {
                "home": float(row[col_h]),
                "draw": float(row[col_d]),
                "away": float(row[col_a])
            }
            
            # Check if exists
            existing = self.db.query(Odds).filter(
                Odds.match_id == match.id,
                Odds.bookmaker == name
            ).first()
            
            if existing:
                existing.odds_data = odds_data
            else:
                layout = Odds(
                    match_id=match.id,
                    bookmaker=name,
                    market="1x2",
                    odds_data=odds_data
                )
                self.db.add(layout)

    def _get_int(self, row, key):
        val = row.get(key)
        if pd.isna(val):
            return None
        try:
            return int(val)
        except:
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = FootballDataCoUkCollector()
    collector.sync_season("2526") # Try current
    # collector.sync_season("2425") # Try previous
