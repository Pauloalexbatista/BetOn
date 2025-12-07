from datetime import datetime
from typing import List, Dict

class RiskManager:
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.DRAWDOWN_LIMIT = 0.20  # 20%
        self.EXPOSURE_LIMIT = 0.15  # 15% of current bankroll
        self.LOSING_STREAK_LIMIT = 5

    def check_risk(self, current_balance: float, active_exposure: float, bet_history: List[Dict]) -> List[str]:
        alerts = []

        # 1. Drawdown Check
        drawdown = (self.initial_balance - current_balance) / self.initial_balance
        if drawdown >= self.DRAWDOWN_LIMIT:
            alerts.append(f"⚠️ High Drawdown Warning: {drawdown*100:.1f}% (Limit: {self.DRAWDOWN_LIMIT*100}%)")

        # 2. Exposure Check
        exposure_ratio = active_exposure / current_balance if current_balance > 0 else 1.0
        if exposure_ratio >= self.EXPOSURE_LIMIT:
             alerts.append(f"⚠️ High Exposure Warning: {exposure_ratio*100:.1f}% locked (Limit: {self.EXPOSURE_LIMIT*100}%)")

        # 3. Losing Streak Check
        streak = 0
        for bet in sorted(bet_history, key=lambda x: x['placed_at'], reverse=True):
            if bet['status'] == 'lost':
                streak += 1
            elif bet['status'] == 'won':
                break
        
        if streak >= self.LOSING_STREAK_LIMIT:
            alerts.append(f"🛑 Stop Loss Warning: {streak} consecutive losses")

        return alerts
