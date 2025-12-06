from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Betfair API
    betfair_username: str = ""
    betfair_password: str = ""
    betfair_app_key: str = ""
    betfair_cert_path: str = "./certs/client-2048.crt"
    betfair_key_path: str = "./certs/client-2048.key"
    
    # API-Football
    api_football_key: str = ""
    api_football_base_url: str = "https://v3.football.api-sports.io"
    
    # TheOddsAPI
    the_odds_api_key: str = ""
    the_odds_api_base_url: str = "https://api.the-odds-api.com/v4"
    
    # Database
    database_url: str = "sqlite:///./beton.db"
    
    # Bankroll
    initial_bankroll: float = 1000.0
    max_stake_percentage: float = 5.0
    stop_loss_percentage: float = 20.0
    
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
