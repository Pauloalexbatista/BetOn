from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from database.database import get_db
from database.models import Bet, BankrollHistory, BankrollSettings
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

class SetBalanceRequest(BaseModel):
    new_balance: float

class AdjustBalanceRequest(BaseModel):
    adjustment: float  # Can be positive or negative

class SetStakePercentageRequest(BaseModel):
    stake_percentage: float  # 0-100

class SetMaxExposureRequest(BaseModel):
    max_exposure: float

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

# New Bankroll Settings Endpoints

@router.get("/settings")
def get_bankroll_settings(db: Session = Depends(get_db)):
    """Get current bankroll settings"""
    settings = db.query(BankrollSettings).first()
    if not settings:
        # Create default settings if none exist
        settings = BankrollSettings(
            initial_balance=1000.0,
            default_stake_percentage=2.0,
            max_exposure=200.0
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "initial_balance": settings.initial_balance,
        "default_stake_percentage": settings.default_stake_percentage,
        "max_exposure": settings.max_exposure,
        "updated_at": settings.updated_at
    }

@router.post("/set-balance")
def set_balance(req: SetBalanceRequest, db: Session = Depends(get_db)):
    """Set new bankroll balance"""
    if req.new_balance < 0:
        raise HTTPException(status_code=400, detail="Balance cannot be negative")
    
    settings = db.query(BankrollSettings).first()
    if not settings:
        settings = BankrollSettings()
        db.add(settings)
    
    old_balance = settings.initial_balance
    settings.initial_balance = req.new_balance
    db.commit()
    
    # Log the change in history
    history_entry = BankrollHistory(
        balance=req.new_balance,
        change=req.new_balance - old_balance,
        reason="balance_set",
        notes=f"Balance manually set from €{old_balance:.2f} to €{req.new_balance:.2f}"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "success": True,
        "new_balance": req.new_balance,
        "previous_balance": old_balance,
        "message": f"Balance updated to €{req.new_balance:.2f}"
    }

@router.post("/adjust-balance")
def adjust_balance(req: AdjustBalanceRequest, db: Session = Depends(get_db)):
    """Adjust bankroll balance by a positive or negative amount"""
    settings = db.query(BankrollSettings).first()
    if not settings:
        settings = BankrollSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    new_balance = settings.initial_balance + req.adjustment
    
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Adjusted balance cannot be negative")
    
    old_balance = settings.initial_balance
    settings.initial_balance = new_balance
    db.commit()
    
    # Log the adjustment
    adjustment_type = "increased" if req.adjustment > 0 else "decreased"
    history_entry = BankrollHistory(
        balance=new_balance,
        change=req.adjustment,
        reason="balance_adjusted",
        notes=f"Balance {adjustment_type} by €{abs(req.adjustment):.2f}"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "success": True,
        "new_balance": new_balance,
        "adjustment": req.adjustment,
        "message": f"Balance {adjustment_type} by €{abs(req.adjustment):.2f}"
    }

@router.post("/set-stake-percentage")
def set_stake_percentage(req: SetStakePercentageRequest, db: Session = Depends(get_db)):
    """Set default stake percentage"""
    if req.stake_percentage < 0 or req.stake_percentage > 100:
        raise HTTPException(status_code=400, detail="Stake percentage must be between 0 and 100")
    
    settings = db.query(BankrollSettings).first()
    if not settings:
        settings = BankrollSettings()
        db.add(settings)
    
    settings.default_stake_percentage = req.stake_percentage
    db.commit()
    db.refresh(settings)
    
    stake_amount = (settings.initial_balance * req.stake_percentage / 100)
    
    return {
        "success": True,
        "stake_percentage": req.stake_percentage,
        "stake_amount": round(stake_amount, 2),
        "message": f"Default stake set to {req.stake_percentage}% (€{stake_amount:.2f})"
    }

@router.post("/set-max-exposure")
def set_max_exposure(req: SetMaxExposureRequest, db: Session = Depends(get_db)):
    """Set maximum exposure limit"""
    if req.max_exposure < 0:
        raise HTTPException(status_code=400, detail="Max exposure cannot be negative")
    
    settings = db.query(BankrollSettings).first()
    if not settings:
        settings = BankrollSettings()
        db.add(settings)
    
    settings.max_exposure = req.max_exposure
    db.commit()
    db.refresh(settings)
    
    percent_of_bankroll = (req.max_exposure / settings.initial_balance * 100) if settings.initial_balance > 0 else 0
    
    return {
        "success": True,
        "max_exposure": req.max_exposure,
        "percent_of_bankroll": round(percent_of_bankroll, 1),
        "message": f"Max exposure set to €{req.max_exposure:.2f} ({percent_of_bankroll:.1f}%)"
    }
