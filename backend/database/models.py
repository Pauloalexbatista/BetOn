from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String)
    away_team = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    league_id = Column(Integer)
    season = Column(Integer)
    home_elo = Column(Integer)
    away_elo = Column(Integer)
    status = Column(String)
    result = Column(String)
    odds_history = relationship("OddsHistory", back_populates="match")

class OddsHistory(Base):
    __tablename__ = "odds_history"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    market_type = Column(String)
    odd_value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    match = relationship("Match", back_populates="odds_history")

class SimulatedBet(Base):
    __tablename__ = "simulated_bets"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    strategy_name = Column(String)
    stake = Column(Float)
    odd_taken = Column(Float)
    passo_martingale = Column(Integer, nullable=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)