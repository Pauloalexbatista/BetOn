from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import Strategy, StrategyCondition

router = APIRouter()

# --- Pydantic Models ---

class ConditionBase(BaseModel):
    entity: str
    context: str
    metric: str
    operator: str
    value: float
    last_n_games: int = 5

class ConditionCreate(ConditionBase):
    pass

class ConditionResponse(ConditionBase):
    id: int
    strategy_id: int
    
    class Config:
        from_attributes = True

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_outcome: str = "home_win"
    is_active: bool = True
    leagues: Optional[List[str]] = None
    teams: Optional[List[str]] = None

class StrategyCreate(StrategyBase):
    conditions: List[ConditionCreate] = []

class StrategyResponse(StrategyBase):
    id: int
    created_at: datetime
    conditions: List[ConditionResponse]
    
    class Config:
        from_attributes = True

class StrategyPreview(BaseModel):
    """Model for strategy preview request"""
    conditions: List[ConditionCreate]
    target_outcome: str
    leagues: Optional[List[str]] = None
    teams: Optional[List[str]] = None
    limit: Optional[int] = 100

# --- API Endpoints ---

@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new betting strategy with conditions"""
    try:
        # 1. Create Strategy Header
        db_strategy = Strategy(
            name=strategy.name,
            description=strategy.description,
            target_outcome=strategy.target_outcome,
            is_active=strategy.is_active,
            leagues=strategy.leagues,
            teams=strategy.teams
        )
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        
        # 2. Create Conditions
        for condition in strategy.conditions:
            db_condition = StrategyCondition(
                strategy_id=db_strategy.id,
                entity=condition.entity,
                context=condition.context,
                metric=condition.metric,
                operator=condition.operator,
                value=condition.value,
                last_n_games=condition.last_n_games
            )
            db.add(db_condition)
        
        db.commit()
        db.refresh(db_strategy)
        return db_strategy
    except Exception as e:
        print(f"ERROR create_strategy: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(db: Session = Depends(get_db)):
    """List all strategies"""
    try:
        # Debug print
        print("Executing list_strategies...")
        strategies = db.query(Strategy).all()
        print(f"Found {len(strategies)} strategies")
        return strategies
    except Exception as e:
        print(f"ERROR list_strategies: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get single strategy details"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.put("/{strategy_id}/toggle", response_model=StrategyResponse)
async def toggle_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Toggle strategy active status"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = not strategy.is_active
    db.commit()
    db.refresh(strategy)
    return strategy

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted id={}".format(strategy_id)}

@router.post("/{strategy_id}/backtest")
async def run_backtest(strategy_id: int, db: Session = Depends(get_db)):
    """Run backtest for a specific strategy"""
    try:
        from analysis.backtester import Backtester
        
        # Initialize and Run
        engine = Backtester(db)
        results = engine.run(strategy_id)
        
        return results
    except Exception as e:
        print(f"ERROR run_backtest: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview")
async def preview_strategy(preview_data: StrategyPreview, db: Session = Depends(get_db)):
    """
    Quick preview of strategy performance without saving
    Returns estimated metrics based on recent matches
    """
    try:
        from analysis.strategy_preview import StrategyPreviewEngine
        
        # Convert conditions to dict format
        conditions_dict = [cond.dict() for cond in preview_data.conditions]
        
        # Initialize preview engine
        engine = StrategyPreviewEngine(db)
        
        # Run preview
        results = engine.run_preview(
            conditions=conditions_dict,
            target_outcome=preview_data.target_outcome,
            leagues=preview_data.leagues,
            teams=preview_data.teams,
            limit=preview_data.limit or 100
        )
        
        return results
    except Exception as e:
        print(f"ERROR preview_strategy: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
