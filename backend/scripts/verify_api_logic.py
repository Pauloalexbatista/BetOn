from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Mock SQLAlchemy Objects
class MockCondition:
    def __init__(self):
        self.id = 1
        self.strategy_id = 1
        self.entity = "home_team"
        self.context = "home"
        self.metric = "goals"
        self.operator = ">"
        self.value = 1.5
        self.last_n_games = 5

class MockStrategy:
    def __init__(self):
        self.id = 1
        self.name = "Test"
        self.description = "Desc"
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.conditions = [MockCondition()]

# Pydantic Models (Copied from strategies.py)
class ConditionBase(BaseModel):
    entity: str
    context: str
    metric: str
    operator: str
    value: float
    last_n_games: int = 5

class ConditionResponse(ConditionBase):
    id: int
    strategy_id: int
    class Config:
        from_attributes = True

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class StrategyResponse(StrategyBase):
    id: int
    created_at: datetime
    conditions: List[ConditionResponse]
    class Config:
        from_attributes = True

def test():
    print("Testing Pydantic Serialization...")
    try:
        mock_strat = MockStrategy()
        response = StrategyResponse.model_validate(mock_strat)
        print("Success!")
        print(response.json())
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
