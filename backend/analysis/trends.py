import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Match, Team, Odds
import pandas as pd

def analyze_trends():
    db = SessionLocal()
    
    # 1. League Overview
    print("\n📊 PORTUGUESE LEAGUE ANALYSIS (2019-2024)")
    print("==========================================")
    
    total_matches = db.query(Match).filter(Match.status == "finished").count()
    home_wins = db.query(Match).filter(Match.home_score > Match.away_score).count()
    draws = db.query(Match).filter(Match.home_score == Match.away_score).count()
    away_wins = db.query(Match).filter(Match.away_score > Match.home_score).count()
    
    print(f"Total Matches: {total_matches}")
    print(f"🏠 Home Wins: {home_wins} ({round(home_wins/total_matches*100, 1)}%)")
    print(f"🤝 Draws:      {draws} ({round(draws/total_matches*100, 1)}%)")
    print(f"✈️ Away Wins:  {away_wins} ({round(away_wins/total_matches*100, 1)}%)")
    
    # 2. Goals Analysis
    total_goals = db.query(func.sum(Match.home_score + Match.away_score)).scalar()
    avg_goals = total_goals / total_matches
    print(f"⚽ Avg Goals/Game: {round(avg_goals, 2)}")
    
    over_25 = 0
    btts = 0
    all_matches = db.query(Match).filter(Match.status == "finished").all()
    
    for m in all_matches:
        if (m.home_score + m.away_score) > 2.5:
            over_25 += 1
        if m.home_score > 0 and m.away_score > 0:
            btts += 1
            
    print(f"📈 Over 2.5 Goals: {over_25} ({round(over_25/total_matches*100, 1)}%)")
    print(f"🥅 BTTS (Both Score): {btts} ({round(btts/total_matches*100, 1)}%)")

    # 3. Most Profitable Teams (To Back Blindly)
    print("\n💰 MOST PROFITABLE TEAMS (ROI)")
    print("If you bet €10 on WIN for every game:")
    print("------------------------------------------")
    
    teams = db.query(Team).all()
    team_roi = []
    
    for team in teams:
        matches = db.query(Match).filter(
            (Match.home_team_id == team.id) | 
            (Match.away_team_id == team.id)
        ).filter(Match.status == "finished").all()
        
        balance = 0
        invested = 0
        wins = 0
        
        for m in matches:
            if not m.odds: continue
            
            # Simple odds lookup (Bet365 usually)
            odds_obj = next((o for o in m.odds if o.bookmaker == "Bet365" and o.odds_data), None)
            if not odds_obj: continue
            
            odds_data = odds_obj.odds_data
            odds_val = 0
            
            is_home = m.home_team_id == team.id
            won = False
            
            if is_home:
                odds_val = odds_data.get('home', 0)
                if m.home_score > m.away_score: won = True
            else:
                odds_val = odds_data.get('away', 0)
                if m.away_score > m.home_score: won = True
                
            if odds_val > 1.0:
                invested += 10
                if won:
                    balance += 10 * (odds_val - 1)
                    wins += 1
                else:
                    balance -= 10
        
        if invested > 100: # Min 10 games
            roi = (balance / invested) * 100
            team_roi.append({
                "team": team.name, 
                "roi": roi, 
                "profit": balance,
                "win_rate": (wins/(invested/10))*100
            })

    # Sort by ROI
    team_roi.sort(key=lambda x: x['roi'], reverse=True)
    
    print(f"{'TEAM':<20} | {'ROI':<8} | {'PROFIT':<8} | {'WIN RATE'}")
    for t in team_roi[:10]: # Top 10
        print(f"{t['team']:<20} | {t['roi']:>6.1f}% | €{t['profit']:>6.1f}  | {t['win_rate']:.1f}%")
        
    print("\n📉 LEAST PROFITABLE TEAMS (Don't Bet!)")
    for t in team_roi[-5:]:
        print(f"{t['team']:<20} | {t['roi']:>6.1f}% | €{t['profit']:>6.1f}")

    db.close()

if __name__ == "__main__":
    analyze_trends()
