import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from analysis.backtester import Backtester

def verify_strategy():
    db = SessionLocal()
    backtester = Backtester(db)
    
    print("\n🧪 Testing 'Big 3' Strategy (2019-2024)")
    print("Strategy: Bet €10 on Win for SL Benfica/Benfica, FC Porto/Porto, Sporting CP/Sp Lisbon")
    print("Rule: Skip heavy weight clashes (Derbies)")
    print("------------------------------------------------")
    
    # Include both API and CSV naming conventions
    results = backtester.run_strategy(["SL Benfica", "Benfica", "FC Porto", "Porto", "Sporting CP", "Sp Lisbon"])
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return

    print(f"💰 Final Balance: €{results['final_balance']} (Start: €1000)")
    print(f"📈 Total Profit: €{results['total_profit']}")
    print(f"📊 ROI: {results['roi']}%")
    print(f"🎲 Total Bets: {results['total_bets']}")
    print(f"✅ Wins: {results['won_bets']} ({results['win_rate']}%)")
    
    print("\n🔍 Last 5 Bets:")
    for bet in results['history'][-5:]:
        print(f"   {bet['date'].date()} | {bet['match']} | {bet['selection']} @ {bet['odds']} | {bet['result']} | Bal: €{bet['balance']}")

    db.close()

if __name__ == "__main__":
    verify_strategy()
