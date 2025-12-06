from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database.models import Strategy
from pydantic import BaseModel

router = APIRouter()


class StrategyCreate(BaseModel):
    name: str
    description: str | None = None
    strategy_type: str
    config: dict = {}
    is_active: bool = False


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: str | None
    strategy_type: str
    config: dict
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy_data: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new betting strategy"""
    # Check if name already exists
    existing = db.query(Strategy).filter(Strategy.name == strategy_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Strategy name already exists")
    
    strategy = Strategy(**strategy_data.dict())
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    is_active: bool | None = None,
    db: Session = Depends(get_db)
):
    """Get all strategies"""
    query = db.query(Strategy)
    
    if is_active is not None:
        query = query.filter(Strategy.is_active == is_active)
    
    strategies = query.all()
    return strategies


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get strategy details"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.patch("/{strategy_id}/toggle")
async def toggle_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Toggle strategy active status"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = not strategy.is_active
    db.commit()
    
    return {"id": strategy.id, "is_active": strategy.is_active}
