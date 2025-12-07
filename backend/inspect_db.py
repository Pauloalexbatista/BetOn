from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Match, Team
from database.database import Base

# Setup DB connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./beton.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def inspect_data():
    print("-" * 50)
    print("TEAMS (Top 5):")
    teams = db.query(Team).limit(5).all()
    for team in teams:
        print(f"ID: {team.id} | Name: {team.name} | League: {team.league}")

    print("-" * 50)
    print("MATCHES (Top 5):")
    matches = db.query(Match).limit(5).all()
    for match in matches:
        home = db.query(Team).filter(Team.id == match.home_team_id).first()
        away = db.query(Team).filter(Team.id == match.away_team_id).first()
        home_name = home.name if home else "Unknown"
        away_name = away.name if away else "Unknown"
        print(f"Date: {match.match_date} | {home_name} vs {away_name} | Score: {match.home_score}-{match.away_score}")
    
    print("-" * 50)
    total_teams = db.query(Team).count()
    total_matches = db.query(Match).count()
    print(f"TOTAL: {total_teams} Teams, {total_matches} Matches")

if __name__ == "__main__":
    inspect_data()
