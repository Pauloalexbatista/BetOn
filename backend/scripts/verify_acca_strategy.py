import sys
import os
from datetime import timedelta
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database.models import Match, Team

def verify_acca_strategy():
    db = SessionLocal()
    
    print("\n🚀 Testing 'Big 3 ACCUMULATOR' Strategy (2019-2024)")
    print("Strategy: Combined Bet (Multipla) on Benfica + Porto + Sporting to WIN")
    print("Rule: Must be in the same 'Gameweek' (approx 4 days window)")
    print("Stake: €10 per accumulator")
    print("------------------------------------------------")

    # 1. Get Team IDs with flexible matching
    all_teams = db.query(Team).all()
    std_names = {}
    
    for t in all_teams:
        name_lower = t.name.lower()
        if "benfica" in name_lower and "benfica b" not in name_lower:
            std_names[t.id] = "Benfica"
        elif "porto" in name_lower and "porto b" not in name_lower:
            std_names[t.id] = "Porto"
        elif "sporting" in name_lower and "sporting b" not in name_lower and "gijon" not in name_lower and "covilha" not in name_lower and "braga" not in name_lower:
             # Exclude Sp Braga if they have "Sporting" in name (usually they are Sp Braga)
             std_names[t.id] = "Sporting"
        elif "sp lisbon" in name_lower:
             std_names[t.id] = "Sporting"

    print(f"DEBUG: Mapped {len(std_names)} team IDs to Big 3.")
    
    # 2. Get All Big 3 Matches
    matches = db.query(Match).filter(
        (Match.home_team_id.in_(std_names.keys())) | 
        (Match.away_team_id.in_(std_names.keys()))
    ).filter(Match.status == "finished").order_by(Match.match_date).all()
    
    # 3. Group by "Gameweek" (Simple clustering by date)
    gameweeks = defaultdict(list)
    
    # Sort matches by date
    matches.sort(key=lambda x: x.match_date)
    
    current_wk_start = matches[0].match_date
    current_wk_id = 0
    
    for m in matches:
        # If match is more than 6 days from start of week, new week
        if (m.match_date - current_wk_start).days > 6:
            current_wk_id += 1
            current_wk_start = m.match_date
            
        gameweeks[current_wk_id].append(m)

    print(f"DEBUG: Found {len(gameweeks)} gameweeks.")
    
    # 4. Simulate Betting
    balance = 1000
    initial_balance = 1000
    stake = 10
    
    total_bets = 0
    won_bets = 0
    history = []
    
    for wk_id, wk_matches in gameweeks.items():
        # Debug small clusters
        # if len(wk_matches) < 3: continue 

        # Check who is the Big 3 team
        week_teams = set()
        has_derby = False
        
        involved_matches = {} # Team -> Match
        
        for m in wk_matches:
            b3_team = None
            # Check ID -> Std Name mapping
            if m.home_team_id in std_names: b3_team = std_names[m.home_team_id]
            if m.away_team_id in std_names: 
                if b3_team: has_derby = True 
                b3_team = std_names[m.away_team_id]
            
            if b3_team:
                week_teams.add(b3_team)
                involved_matches[b3_team] = m

        # DEBUG: Print first 5 weeks status
        if wk_id < 5:
             print(f"DEBUG: Week {wk_id} has {len(week_teams)} Big 3 teams: {week_teams}")

        if len(week_teams) == 3 and not has_derby:
            # Valid Accumulator Opportunity!
            # Get Odds
            acca_odds = 1.0
            possible = True
            
            selections = []
            
            for team, m in involved_matches.items():
                # Find odds
                price = 0
                won_leg = False
                
                # Determine selection
                is_home = (std_names.get(m.home_team_id) == team)
                
                # Get odd
                odds_record = next((o for o in m.odds if o.bookmaker == "Bet365" and o.odds_data), None)
                if not odds_record:
                    possible = False
                    break
                    
                if is_home:
                    price = odds_record.odds_data.get('home', 0)
                    if m.home_score > m.away_score: won_leg = True
                else:
                    price = odds_record.odds_data.get('away', 0)
                    if m.away_score > m.home_score: won_leg = True
                
                if price < 1.01:
                    possible = False # Bad data
                    break
                    
                acca_odds *= price
                selections.append({
                    "team": team,
                    "price": price,
                    "won": won_leg,
                    "match": f"{m.home_team.name} vs {m.away_team.name}"
                })
            
            if possible:
                total_bets += 1
                
                # Check outcome
                all_won = all(s['won'] for s in selections)
                profit = -stake
                if all_won:
                    profit = (stake * acca_odds) - stake
                    won_bets += 1
                
                balance += profit
                
                history.append({
                    "date": wk_matches[0].match_date.date(),
                    "matches_desc": " | ".join([s['match'] for s in selections]),
                    "odds": round(acca_odds, 2),
                    "result": "WON" if all_won else "LOST",
                    "profit": round(profit, 2),
                    "balance": round(balance, 2)
                })

    # Report
    roi = ((balance - initial_balance) / (total_bets * stake)) * 100 if total_bets > 0 else 0
    win_rate = (won_bets / total_bets) * 100 if total_bets > 0 else 0
    
    print(f"💰 Final Balance: €{round(balance, 2)} (Start: €{initial_balance})")
    print(f"📈 Total Profit: €{round(balance - initial_balance, 2)}")
    print(f"📊 ROI: {round(roi, 2)}%")
    print(f"🎲 Total Accas: {total_bets}")
    print(f"✅ Won Accas: {won_bets} ({round(win_rate, 1)}%)")
    
    # Export to CSV
    import csv
    csv_file = "acca_results.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Matches", "Odds", "Result", "Profit", "Balance"])
        
        for h in history:
            writer.writerow([
                h['date'], 
                h.get('matches_desc', 'N/A'), # We need to add this to history dict first
                h['odds'],
                h['result'],
                h['profit'],
                h['balance']
            ])
            
    print(f"\n📄 Detailed Report saved to: {csv_file}")
    print("You can open this file in Excel to sort and filter!")

    db.close()

if __name__ == "__main__":
    verify_acca_strategy()
