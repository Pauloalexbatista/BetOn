from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Bet, BankrollHistory, Match

class BankrollManager:
    """
    Manages betting capital, tracks exposure, and handles bet placement.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_current_balance(self) -> float:
        """Get the latest confirmed bankroll balance"""
        last_entry = self.db.query(BankrollHistory).order_by(desc(BankrollHistory.timestamp)).first()
        return last_entry.balance if last_entry else 1000.00 # Default start

    def get_active_exposure(self) -> float:
        """Calculate total amount currently currently locked in pending bets"""
        pending_bets = self.db.query(Bet).filter(Bet.status == "pending").all()
        return sum(b.stake for b in pending_bets)

    def place_bet(self, match_id: int, selection: str, odds: float, stake: float, 
                  strategy: str = "Manual", market: str = "Match Odds", 
                  is_paper: bool = True) -> Dict:
        """
        Place a new bet and update bankroll.
        """
        current_bal = self.get_current_balance()
        
        # 1. Validate funds
        if stake > current_bal:
            return {"error": "Insufficient funds"}

        # 2. Create Bet
        new_bet = Bet(
            match_id=match_id,
            selection=selection,
            odds=odds,
            stake=stake,
            market=market,
            status="pending",
            is_paper_trade=is_paper,
            placed_at=datetime.utcnow(),
            notes=f"Strategy: {strategy}"
        )
        self.db.add(new_bet)
        self.db.flush() # Get ID

        # 3. Deduct Stake from Balance (Lock funds)
        new_balance = current_bal - stake
        
        transaction = BankrollHistory(
            balance=new_balance,
            change=-stake,
            reason="bet_placed",
            bet_id=new_bet.id,
            notes=f"Placed bet on {selection} (@{odds})"
        )
        self.db.add(transaction)
        self.db.commit()
        
        return {"success": True, "bet_id": new_bet.id, "new_balance": new_balance}

    def settle_bet(self, bet_id: int, won: bool) -> Dict:
        """
        Settle a pending bet as Won or Lost.
        """
        bet = self.db.query(Bet).filter(Bet.id == bet_id).first()
        if not bet or bet.status != "pending":
            return {"error": "Invalid bet or already settled"}

        current_bal = self.get_current_balance()
        profit = 0.0
        
        if won:
            # Return Stake + Profit
            return_amount = bet.stake * bet.odds
            profit = return_amount - bet.stake
            
            new_balance = current_bal + return_amount
            
            # Update Bet
            bet.status = "won"
            bet.profit_loss = profit
            bet.settled_at = datetime.utcnow()
            
            # Update History
            txn = BankrollHistory(
                balance=new_balance,
                change=return_amount, # Re-add stake + profit
                reason="bet_won",
                bet_id=bet.id,
                notes=f"Won bet #{bet.id} (Profit: +{profit})"
            )
            self.db.add(txn)
            
        else:
            # Lost (Money was already deducted at placement)
            bet.status = "lost"
            bet.profit_loss = -bet.stake
            bet.settled_at = datetime.utcnow()
            
            # No transaction needed as money generated NO return
            # But we might want to log a "settlement" for clarity?
            # Actually, standard is: Placement = -Stake. Win = +Return. Loss = +0.
            # So balance remains what it was after deduction.
            
            # Optional: Log explicitly that it was lost (Change 0) for charts
            # txn = BankrollHistory(balance=current_bal, change=0, reason="bet_lost", bet_id=bet.id)
            # self.db.add(txn)
            
        self.db.commit()
        return {"success": True, "status": bet.status, "profit": profit}
