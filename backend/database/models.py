from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base


class Team(Base):
    """Football team model"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True)  # External API ID
    name = Column(String, nullable=False)
    country = Column(String)
    league = Column(String)
    logo_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")


class Match(Base):
    """Football match model"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, unique=True, index=True) # External API ID
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    league = Column(String)
    season = Column(String)
    round = Column(String, nullable=True) # Gameweek/Round
    match_date = Column(DateTime, nullable=False)
    status = Column(String)  # scheduled, live, finished, postponed
    
    # Results
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    # Detailed Statistics
    home_shots = Column(Integer, nullable=True)     # HS
    away_shots = Column(Integer, nullable=True)     # AS
    home_shots_target = Column(Integer, nullable=True) # HST
    away_shots_target = Column(Integer, nullable=True) # AST
    home_corners = Column(Integer, nullable=True)   # HC
    away_corners = Column(Integer, nullable=True)   # AC
    home_fouls = Column(Integer, nullable=True)     # HF
    away_fouls = Column(Integer, nullable=True)     # AF
    home_yellow = Column(Integer, nullable=True)    # HY
    away_yellow = Column(Integer, nullable=True)    # AY
    home_red = Column(Integer, nullable=True)       # HR
    away_red = Column(Integer, nullable=True)       # AR
    referee = Column(String, nullable=True)
    
    # Statistics (JSON) - Keep for any extras
    statistics = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    odds = relationship("Odds", back_populates="match")
    bets = relationship("Bet", back_populates="match")


class Odds(Base):
    """Betting odds model"""
    __tablename__ = "odds"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    bookmaker = Column(String)  # e.g. pinnacle, bet365
    market = Column(String)  # 1x2, over_under, btts
    
    # Odds values (JSON for flexibility)
    odds_data = Column(JSON)  # {"home": 2.5, "draw": 3.2, "away": 2.8}
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="odds")


class Strategy(Base):
    """Betting strategy configuration"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    target_outcome = Column(String, default="home_win") # home_win, away_win, draw, over_2.5, under_2.5, btts_yes, btts_no
    
    # Scope / Filters
    leagues = Column(JSON, nullable=True) # List of league names e.g. ["Primeira Liga"]
    teams = Column(JSON, nullable=True)   # List of team names e.g. ["FC Porto", "Benfica"]

    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bets = relationship("Bet", back_populates="strategy")
    conditions = relationship("StrategyCondition", back_populates="strategy", cascade="all, delete-orphan")


class StrategyCondition(Base):
    """Atomic rule for a strategy"""
    __tablename__ = "strategy_conditions"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    
    # Rule Definition
    entity = Column(String)  # "home_team", "away_team", "match"
    context = Column(String) # "overall", "home", "away"
    metric = Column(String)  # "win_rate", "goals_scored", "odds"
    operator = Column(String) # ">", "<", "="
    value = Column(Float)    # The threshold value (e.g. 1.5, 0.7)
    last_n_games = Column(Integer, default=5) # Rolling window

    # Relationships
    strategy = relationship("Strategy", back_populates="conditions")


class Bet(Base):
    """Placed bet model"""
    __tablename__ = "bets"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    
    # Bet details
    market = Column(String)  # 1x2, over_under, btts
    selection = Column(String)  # home, draw, away, over, under, yes, no
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    
    # External IDs
    external_bet_id = Column(String)  # ID from the bookmaker/source
    external_market_id = Column(String) # Market ID from the bookmaker/source
    
    # Status
    status = Column(String)  # pending, matched, won, lost, void
    is_paper_trade = Column(Boolean, default=True)
    
    # Results
    profit_loss = Column(Float)
    settled_at = Column(DateTime)
    
    # Metadata
    placed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)
    
    # Relationships
    match = relationship("Match", back_populates="bets")
    strategy = relationship("Strategy", back_populates="bets")


class BankrollHistory(Base):
    """Bankroll tracking history"""
    __tablename__ = "bankroll_history"
    
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, nullable=False)
    change = Column(Float)  # Positive or negative change
    reason = Column(String)  # bet_won, bet_lost, deposit, withdrawal
    bet_id = Column(Integer, ForeignKey("bets.id"), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)
