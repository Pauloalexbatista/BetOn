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
    api_id = Column(Integer, unique=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    league = Column(String)
    season = Column(String)
    match_date = Column(DateTime, nullable=False)
    status = Column(String)  # scheduled, live, finished, postponed
    
    # Results
    home_score = Column(Integer)
    away_score = Column(Integer)
    
    # Statistics (JSON)
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
    bookmaker = Column(String)  # betfair, bet365, etc.
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
    strategy_type = Column(String)  # value_betting, form_based, ml_prediction
    
    # Configuration (JSON)
    config = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bets = relationship("Bet", back_populates="strategy")


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
    
    # Betfair specific
    betfair_bet_id = Column(String)
    betfair_market_id = Column(String)
    
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
