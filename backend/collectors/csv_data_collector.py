import pandas as pd
import logging
import io
import requests
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Team, Match, Odds

logger = logging.getLogger(__name__)

class CSVDataCollector:
    """
    Collector for Football-Data.co.uk CSV files.
    Best source for historical data (Results + Odds).
    """
    
    BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{div}.csv"
    
    def __init__(self, db: Session = None):
        self.db = db if db else SessionLocal()

    def sync_season(self, season_start_year: int, division: str = "P1"):
        """
        Download and sync a full season.
        season_start_year: e.g. 23 for 2023/2024
        """
        # Format season string: 2324
        season_str = f"{season_start_year:02d}{(season_start_year + 1):02d}"
        url = self.BASE_URL.format(season=season_str, div=division)
        
        logger.info(f"Downloading CSV from: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(response.text))
            logger.info(f"Downloaded {len(df)} rows. Processing...")
            
            self._process_dataframe(df, season_str)
            logger.info(f"Season {season_str} synced successfully!")
            return True
            
        except requests.exceptions.HTTPError:
            logger.error(f"Season {season_str} not found (404).")
            return False
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return False

    def _process_dataframe(self, df: pd.DataFrame, season: str):
        """Process rows and update database"""
        
        # Standardize column names if needed
        # Football-Data.co.uk columns: Date, HomeTeam, AwayTeam, FTHG, FTAG, H, D, A (Odds)
        
        for _, row in df.iterrows():
            if pd.isna(row['Date']) or pd.isna(row['HomeTeam']):
                continue
                
            # Parse Date
            try:
                match_date = pd.to_datetime(row['Date'], dayfirst=True).to_pydatetime()
            except:
                continue
                
            home_name = row['HomeTeam']
            away_name = row['AwayTeam']
            
            # 1. Sync Teams
            home_team = self._get_or_create_team(home_name)
            away_team = self._get_or_create_team(away_name)
            
            # 2. Sync Match
            match = self._get_or_create_match(
                home_team, away_team, match_date, season,
                row['FTHG'], row['FTAG'], row['FTR'] # Full Time Result
            )
            
            # 3. Sync Stats (if available)
            if 'HS' in row: # Home Shots
                stats = {
                    "home_shots": row.get('HS'),
                    "away_shots": row.get('AS'),
                    "home_shots_target": row.get('HST'),
                    "away_shots_target": row.get('AST'),
                    "home_corners": row.get('HC'),
                    "away_corners": row.get('AC'),
                    "home_yellow": row.get('HY'),
                    "away_yellow": row.get('AY'),
                    "home_red": row.get('HR'),
                    "away_red": row.get('AR'),
                }
                # Clean NaNs
                stats = {k: v for k, v in stats.items() if pd.notna(v)}
                match.statistics = stats
            
            # 4. Sync Odds (Bet365 usually available as B365H, B365D, B365A)
            if 'B365H' in row and pd.notna(row['B365H']):
                self._save_odds(match, "Bet365", row['B365H'], row['B365D'], row['B365A'])
            
        self.db.commit()

    def _get_or_create_team(self, name: str) -> Team:
        team = self.db.query(Team).filter(Team.name == name).first()
        if not team:
            # We don't have API ID initially for CSV teams, can sync later
            team = Team(name=name, country="Portugal", league="Primeira Liga")
            self.db.add(team)
            self.db.flush() # Get ID
        return team

    def _get_or_create_match(self, home, away, date, season, h_score, a_score, result):
        match = self.db.query(Match).filter(
            Match.home_team_id == home.id,
            Match.away_team_id == away.id,
            Match.match_date == date
        ).first()
        
        score_status = "finished" 
        
        if not match:
            match = Match(
                home_team_id=home.id,
                away_team_id=away.id,
                match_date=date,
                league="Primeira Liga",
                season=season,
                status=score_status,
                home_score=int(h_score) if pd.notna(h_score) else None,
                away_score=int(a_score) if pd.notna(a_score) else None
            )
            self.db.add(match)
        else:
            # Update scores if needed
            if pd.notna(h_score):
                match.home_score = int(h_score)
                match.away_score = int(a_score)
                match.status = score_status
                
        return match

    def _save_odds(self, match, bookmaker, home, draw, away):
        # Check if odds exist
        existing = self.db.query(Odds).filter(
            Odds.match_id == match.id,
            Odds.bookmaker == bookmaker
        ).first()
        
        odds_data = {
            "home": float(home),
            "draw": float(draw),
            "away": float(away)
        }
        
        if existing:
            existing.odds_data = odds_data
        else:
            new_odds = Odds(
                match_id=match.id,
                bookmaker=bookmaker,
                market="1x2",
                odds_data=odds_data,
                timestamp=match.match_date # Approximate
            )
            self.db.add(new_odds)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collector = CSVDataCollector()
    
    # Download last 5 seasons
    current_year = 23 # 2023/2024
    for i in range(5):
        year = current_year - i
        logger.info(f"--- Processing Season {year}/{year+1} ---")
        collector.sync_season(season_start_year=year)
