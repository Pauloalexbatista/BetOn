from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from database.database import get_db
from database.models import Bet, Match, Strategy
from api.filters import BetFilters
from pydantic import BaseModel

router = APIRouter()


class BetCreate(BaseModel):
    match_id: int
    strategy_id: int | None = None
    market: str
    selection: str
    odds: float
    stake: float
    is_paper_trade: bool = True


class MatchResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    date: datetime
    round: str
    
    class Config:
        from_attributes = True

class BetResponse(BaseModel):
    id: int
    match_id: int
    match: MatchResponse | None = None
    market: str
    selection: str
    odds: float
    stake: float
    status: str
    is_paper_trade: bool
    profit_loss: float | None
    placed_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=BetResponse)
async def create_bet(bet_data: BetCreate, db: Session = Depends(get_db)):
    """Place a new bet (paper or real)"""
    # Verify match exists
    match = db.query(Match).filter(Match.id == bet_data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Create bet
    bet = Bet(
        match_id=bet_data.match_id,
        strategy_id=bet_data.strategy_id,
        market=bet_data.market,
        selection=bet_data.selection,
        odds=bet_data.odds,
        stake=bet_data.stake,
        is_paper_trade=bet_data.is_paper_trade,
        status="pending"
    )
    
    db.add(bet)
    db.commit()
    db.refresh(bet)
    
    # Re-fetch with match relationship for response
    # SQLAlchemy lazy loading would work, but this ensures it's populated for Pydantic
    return bet


@router.get("/", response_model=List[BetResponse])
async def get_bets(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    is_paper_trade: bool | None = None,
    filters: BetFilters = Depends(),
    db: Session = Depends(get_db)
):
    """Get all bets with filters"""
    query = db.query(Bet).join(Match)
    
    if status:
        query = query.filter(Bet.status == status)
    if is_paper_trade is not None:
        query = query.filter(Bet.is_paper_trade == is_paper_trade)
        
    query = filters.apply(query)
    
    # Order by placed_at desc
    bets = query.order_by(Bet.placed_at.desc()).offset(skip).limit(limit).all()
    return bets


@router.get("/{bet_id}", response_model=BetResponse)
async def get_bet(bet_id: int, db: Session = Depends(get_db)):
    """Get bet details"""
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bet


@router.get("/stats/summary")
async def get_bet_stats(db: Session = Depends(get_db)):
    """Get betting statistics summary"""
    total_bets = db.query(Bet).count()
    pending_bets = db.query(Bet).filter(Bet.status == "pending").count()
    won_bets = db.query(Bet).filter(Bet.status == "won").count()
    lost_bets = db.query(Bet).filter(Bet.status == "lost").count()
    
    # Calculate total P/L
    total_pl = db.query(Bet).filter(Bet.profit_loss.isnot(None)).with_entities(
        func.sum(Bet.profit_loss)
    ).scalar() or 0.0
    
    win_rate = (won_bets / (won_bets + lost_bets) * 100) if (won_bets + lost_bets) > 0 else 0
    
    # Calculate Total Exposure (sum of stakes for pending bets)
    total_exposure = db.query(Bet).filter(Bet.status == "pending").with_entities(
        func.sum(Bet.stake)
    ).scalar() or 0.0

    # Calculate Current Bankroll
    # Current = Initial + Total P/L (Total P/L includes won/lost bets)
    # Note: pending bets don't affect P/L until settled, but they reduce "available" bankroll
    from config import settings
    initial_bankroll = settings.initial_bankroll
    current_bankroll = initial_bankroll + total_pl
    
    # Available Bankroll = Current - Exposure
    available_bankroll = current_bankroll - total_exposure

    return {
        "total_bets": total_bets,
        "pending": pending_bets,
        "won": won_bets,
        "lost": lost_bets,
        "win_rate": round(win_rate, 2),
        "total_profit_loss": round(total_pl, 2),
        "bankroll": {
            "initial": initial_bankroll,
            "current": round(current_bankroll, 2),
            "exposure": round(total_exposure, 2),
            "available": round(available_bankroll, 2),
            "exposure_percent": round((total_exposure / current_bankroll * 100), 1) if current_bankroll > 0 else 0
        }
    }
