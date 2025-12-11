from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import Strategy, StrategyCondition, Match, Team

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
    strategy_type: str = "single"  # "single" or "accumulator"
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
            strategy_type=strategy.strategy_type,
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
        strategies = db.query(Strategy).all()
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

@router.get("/{strategy_id}/matches")
async def get_strategy_matches(
    strategy_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get historical matches that match this strategy"""
    try:
        from analysis.strategy_preview import StrategyPreviewEngine
        
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Convert conditions to dict
        conditions_dict = [
            {
                "entity": c.entity,
                "context": c.context,
                "metric": c.metric,
                "operator": c.operator,
                "value": c.value,
                "last_n_games": c.last_n_games
            }
            for c in strategy.conditions
        ]
        
        # Run preview to get historical matches
        engine = StrategyPreviewEngine(db)
        results = engine.run_preview(
            conditions=conditions_dict,
            target_outcome=strategy.target_outcome,
            leagues=strategy.leagues,
            teams=strategy.teams,
            limit=limit
        )
        
        return {
            "strategy": {
                "id": strategy.id,
                "name": strategy.name,
                "type": strategy.strategy_type
            },
            "stats": {
                "total_matches": results["matches_found"],
                "win_rate": results["win_rate"],
                "roi": results["roi_estimate"],
                "total_profit": results["total_profit"]
            },
            "matches": results["sample_matches"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR get_strategy_matches: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}/upcoming")
async def get_strategy_upcoming(
    strategy_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get upcoming matches for this strategy"""
    try:
        from analysis.strategy_preview import StrategyPreviewEngine
        
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Convert conditions to dict
        conditions_dict = [
            {
                "entity": c.entity,
                "context": c.context,
                "metric": c.metric,
                "operator": c.operator,
                "value": c.value,
                "last_n_games": c.last_n_games
            }
            for c in strategy.conditions
        ]
        
        # Get upcoming matches
        engine = StrategyPreviewEngine(db)
        upcoming = engine.get_upcoming_matches(
            conditions=conditions_dict,
            target_outcome=strategy.target_outcome,
            leagues=strategy.leagues,
            teams=strategy.teams,
            limit=limit
        )
        
        return {
            "strategy": {
                "id": strategy.id,
                "name": strategy.name,
                "type": strategy.strategy_type
            },
            "upcoming": upcoming["matches"],
            "accumulators": upcoming.get("accumulators", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR get_strategy_upcoming: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
    return {"message": f"Strategy deleted id={strategy_id}"}

@router.post("/{strategy_id}/backtest")
async def run_backtest(strategy_id: int, db: Session = Depends(get_db)):
    """Run backtest for a specific strategy"""
    try:
        from analysis.backtester import Backtester
        
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

@router.get("/recommendations")
async def get_recommendations(
    top_20_only: bool = False,
    season: Optional[str] = None,
    market: str = "win_rate",
    min_confidence: float = 0.0,
    db: Session = Depends(get_db)
):
    """
    Get team recommendations with Pareto filtering and confidence scores
    """
    try:
        import sys
        import os
        
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from analysis.pareto_analyzer import ParetoAnalyzer
        from database.models import Team
        
        db_path = os.path.join(backend_path, 'beton.db')
        analyzer = ParetoAnalyzer(db_path=db_path)
        
        top_20_ids = []
        if top_20_only:
            top_20_ids = analyzer.get_top_20_percent_team_ids(
                season=season,
                market=market,
                min_matches=5
            )
        
        if top_20_only and top_20_ids:
            teams = db.query(Team).filter(Team.id.in_(top_20_ids)).all()
        else:
            teams = db.query(Team).all()
        
        recommendations = []
        for team in teams:
            confidence_data = analyzer.calculate_confidence_score(
                team_id=team.id,
                market=market,
                last_n=5
            )
            
            if confidence_data['confidence'] < min_confidence:
                continue
            
            is_top_20 = team.id in top_20_ids if top_20_ids else False
            
            recommendations.append({
                'team_id': team.id,
                'team_name': team.name,
                'confidence': confidence_data['confidence'],
                'is_top_20': is_top_20,
                'breakdown': confidence_data['breakdown'],
                'market': market
            })
        
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'total_teams': len(recommendations),
            'top_20_only': top_20_only,
            'season': season or 'All Seasons',
            'market': market,
            'min_confidence': min_confidence,
            'recommendations': recommendations
        }
        
    except Exception as e:
        print(f"ERROR get_recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
