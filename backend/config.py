from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./beton.db"
    
    # Bankroll
    initial_bankroll: float = 1000.0
    max_stake_percentage: float = 5.0
    stop_loss_percentage: float = 20.0
    
    # APIs
    api_football_key: str = ""
    api_football_base_url: str = "https://v3.football.api-sports.io"

    # The Odds API
    the_odds_api_key: str = ""
    the_odds_api_base_url: str = "https://api.the-odds-api.com/v4"

    # Automation
    paper_trading_mode: bool = True
    auto_bet_enabled: bool = False
    min_value_edge: float = 5.0
    
    # Notifications
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_notifications: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
