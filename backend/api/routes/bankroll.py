from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.database import get_db
from database.models import BankrollHistory, Bet
from pydantic import BaseModel

router = APIRouter()


class BankrollResponse(BaseModel):
    current_balance: float
    total_profit_loss: float
    total_bets: int
    roi_percentage: float


@router.get("/current", response_model=BankrollResponse)
async def get_current_bankroll(db: Session = Depends(get_db)):
    """Get current bankroll status"""
    # Get latest balance
    latest = db.query(BankrollHistory).order_by(
        BankrollHistory.timestamp.desc()
    ).first()
    
    current_balance = latest.balance if latest else 0.0
    
    # Calculate total P/L from bets
    total_pl = db.query(func.sum(Bet.profit_loss)).filter(
        Bet.profit_loss.isnot(None)
    ).scalar() or 0.0
    
    # Count total bets
    total_bets = db.query(Bet).count()
    
    # Calculate ROI
    initial_balance = 1000.0  # TODO: Get from config
    roi = ((current_balance - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
    
    return {
        "current_balance": round(current_balance, 2),
        "total_profit_loss": round(total_pl, 2),
        "total_bets": total_bets,
        "roi_percentage": round(roi, 2)
    }


@router.get("/history")
async def get_bankroll_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get bankroll history"""
    history = db.query(BankrollHistory).order_by(
        BankrollHistory.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": h.id,
            "balance": h.balance,
            "change": h.change,
            "reason": h.reason,
            "timestamp": h.timestamp
        }
        for h in history
    ]
