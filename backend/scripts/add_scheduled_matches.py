"""
Manually add scheduled matches for Primeira Liga 2024/2025
Based on next rounds (15-20)
"""
import sys
sys.path.insert(0, '/app')

from database.database import SessionLocal
from database.models import Match, Team
from datetime import datetime

def get_or_create_team(db, name):
    team = db.query(Team).filter(Team.name == name).first()
    if not team:
        team = Team(name=name, league="Primeira Liga", country="Portugal")
        db.add(team)
        db.flush()
    return team

def main():
    db = SessionLocal()
    
    try:
        # Jornada 15 (próxima jornada exemplo)
        # Baseado no calendário típico da Primeira Liga
        scheduled_matches = [
            # Jornada 15
            ("Sporting", "Benfica", 15, "2024-12-29"),
            ("Porto", "Braga", 15, "2024-12-29"),
            ("Vitória SC", "Casa Pia", 15, "2024-12-29"),
            
            # Jornada 16
            ("Benfica", "Rio Ave", 16, "2025-01-05"),
            ("Sporting", "Moreirense", 16, "2025-01-05"),
            ("Braga", "Porto", 16, "2025-01-05"),
            
            # Jornada 17
            ("Porto", "Benfica", 17, "2025-01-12"),
            ("Sporting", "Famalicão", 17, "2025-01-12"),
            ("Santa Clara", "Braga", 17, "2025-01-12"),
            
            # Jornada 18
            ("Benfica", "Sporting", 18, "2025-01-19"),
            ("Porto", "Vitória SC", 18, "2025-01-19"),
            ("Braga", "Estoril", 18, "2025-01-19"),
        ]
        
        created = 0
        season = "2024/2025"
        
        for home, away, round_num, date_str in scheduled_matches:
            # Get teams
            home_team = get_or_create_team(db, home)
            away_team = get_or_create_team(db, away)
            
            # Check if exists
            existing = db.query(Match).filter(
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
                Match.season == season,
                Match.round == round_num
            ).first()
            
            if not existing:
                # Create
                match_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                new_match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    league="Primeira Liga",
                    season=season,
                    round=round_num,
                    match_date=match_date,
                    status='scheduled'
                )
                db.add(new_match)
                created += 1
                print(f"✅ Created: {home} vs {away} (R{round_num})")
        
        db.commit()
        print(f"\n📊 Total created: {created} scheduled matches")
        
        # Verify
        total_scheduled = db.query(Match).filter(Match.status == 'scheduled').count()
        print(f"✅ Total scheduled in DB: {total_scheduled}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
