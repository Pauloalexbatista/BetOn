from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from database.database import get_db
from database.models import Bet, BankrollHistory
from bankroll.manager import BankrollManager
from bankroll.kelly import calculate_kelly_stake
from bankroll.risk import RiskManager

router = APIRouter()

# Schemas
class BetPlacement(BaseModel):
    match_id: int
    selection: str # "Home", "Away", "Over 2.5", etc
    market: str
    odds: float
    stake: float
    strategy: str = "Manual"

class BetSettlement(BaseModel):
    won: bool

class KellyRequest(BaseModel):
    odds: float
    probability: float # 0.0 - 1.0

# Endpoints

@router.get("/summary")
def get_bankroll_summary(db: Session = Depends(get_db)):
    """Get current balance and exposure"""
    mgr = BankrollManager(db)
    return {
        "current_balance": mgr.get_current_balance(),
        "active_exposure": mgr.get_active_exposure(),
        "currency": "EUR"
    }

@router.get("/alerts")
def get_risk_alerts(db: Session = Depends(get_db)):
    """Get active risk alerts"""
    mgr = BankrollManager(db)
    risk = RiskManager()
    
    current_bal = mgr.get_current_balance()
    exposure = mgr.get_active_exposure()
    history = [
        {"placed_at": b.placed_at, "status": b.status} 
        for b in db.query(Bet).filter(Bet.status.in_(['won', 'lost'])).all()
    ]
    
    warnings = risk.check_risk(current_bal, exposure, history)
    return {"alerts": warnings}

@router.get("/active-bets")
def get_active_bets(db: Session = Depends(get_db)):
    """Get all pending bets"""
    return db.query(Bet).filter(Bet.status == "pending").order_by(Bet.placed_at.desc()).all()

@router.get("/all-bets")
def get_all_bets(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent bets"""
    return db.query(Bet).order_by(Bet.placed_at.desc()).limit(limit).all()

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    """Get recent bankroll transactions"""
    return db.query(BankrollHistory).order_by(BankrollHistory.timestamp.desc()).limit(50).all()

@router.post("/bets")
def place_bet(bet: BetPlacement, db: Session = Depends(get_db)):
    """Place a new bet (Manual or Auto)"""
    mgr = BankrollManager(db)
    result = mgr.place_bet(
        match_id=bet.match_id,
        selection=bet.selection,
        odds=bet.odds,
        stake=bet.stake,
        strategy=bet.strategy,
        market=bet.market
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/bets/{bet_id}/settle")
def settle_bet(bet_id: int, settlement: BetSettlement, db: Session = Depends(get_db)):
    """Settle a bet (Won/Lost)"""
    mgr = BankrollManager(db)
    result = mgr.settle_bet(bet_id, settlement.won)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/bets/{bet_id}")
def delete_bet(bet_id: int, db: Session = Depends(get_db)):
    """Delete a pending bet (Cancel)"""
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    
    if bet.status != "pending":
        raise HTTPException(status_code=400, detail="Can only delete pending bets")
        
    # Refund stake to history/balance
    # We need to reverse the initial transaction
    mgr = BankrollManager(db)
    current_bal = mgr.get_current_balance()
    
    # Refund
    refund_txn = BankrollHistory(
        balance=current_bal + bet.stake,
        change=bet.stake,
        reason="bet_cancelled",
        bet_id=bet.id,
        notes=f"Cancelled bet #{bet.id}"
    )
    db.add(refund_txn)
    db.delete(bet) # Actually delete the bet or mark as cancelled? 
    # Usually better to mark as cancelled, but user said "delete". 
    # Let's actually DELETE for now to keep table clean as requested.
    db.commit()
    return {"success": True, "message": "Bet deleted and stake refunded"}

@router.post("/kelly")
def calculate_kelly(req: KellyRequest, db: Session = Depends(get_db)):
    """Calculate recommended stake"""
    mgr = BankrollManager(db)
    balance = mgr.get_current_balance()
    stake = calculate_kelly_stake(balance, req.odds, req.probability)
    return {
        "recommended_stake": stake,
        "bankroll": balance,
        "percent": round((stake/balance)*100, 2) if balance > 0 else 0
    }
