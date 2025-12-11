"""
Pytest configuration and fixtures for BetOn tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

@pytest.fixture(scope="function")
def test_db():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_odds_api_response():
    """Mock response from The Odds API"""
    return [
        {
            "id": "test_match_1",
            "sport_key": "soccer_portugal_primeira_liga",
            "commence_time": "2025-12-15T19:00:00Z",
            "home_team": "FC Porto",
            "away_team": "Benfica",
            "bookmakers": [
                {
                    "key": "bet365",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "FC Porto", "price": 2.10},
                                {"name": "Benfica", "price": 3.40},
                                {"name": "Draw", "price": 3.20}
                            ]
                        }
                    ]
                }
            ]
        }
    ]
