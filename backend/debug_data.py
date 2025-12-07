from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Team, Match, Odds
import collections

DATABASE_URL = "sqlite:///./beton.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("--- Debugging Data ---")

# 1. Check Team Names
print("\nChecking Team Names:")
teams = db.query(Team).all()
relevant_teams = ["Benfica", "Porto", "Sporting"]
found_teams = {}

for t in teams:
    for target in relevant_teams:
        if target.lower() in t.name.lower():
            print(f" - Found: '{t.name}' (ID: {t.id})")
            found_teams[t.id] = t.name

# 2. Check Matches for these teams
print(f"\nMatches for found teams: {list(found_teams.values())}")
matches = db.query(Match).filter(
    (Match.home_team_id.in_(found_teams.keys())) | 
    (Match.away_team_id.in_(found_teams.keys()))
).all()
print(f"Total Matches Found: {len(matches)}")

# 3. Check Odds for these matches
matches_with_odds = 0
matches_with_bet365 = 0

for m in matches:
    if m.odds:
        matches_with_odds += 1
        for o in m.odds:
            if o.bookmaker == "Bet365":
                matches_with_bet365 += 1
                break

print(f"Matches with ANY odds: {matches_with_odds}")
print(f"Matches with Bet365 odds: {matches_with_bet365}")

db.close()
