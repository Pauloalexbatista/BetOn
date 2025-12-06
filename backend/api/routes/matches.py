from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database.database import get_db
from database.models import Match, Team
from pydantic import BaseModel

router = APIRouter()


class TeamResponse(BaseModel):
    id: int
    name: str
    country: str | None
    league: str | None
    
    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    home_team: TeamResponse
    away_team: TeamResponse
    league: str
    match_date: datetime
    status: str
    home_score: int | None
    away_score: int | None
    
    class Config:
        from_attributes = True


@router.get("/upcoming", response_model=List[MatchResponse])
async def get_upcoming_matches(
    days: int = 7,
    league: str | None = None,
    db: Session = Depends(get_db)
):
    """Get upcoming matches for the next N days"""
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days)
    
    query = db.query(Match).filter(
        Match.match_date >= start_date,
        Match.match_date <= end_date,
        Match.status == "scheduled"
    )
    
    if league:
        query = query.filter(Match.league == league)
    
    matches = query.order_by(Match.match_date).all()
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match details by ID"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """Get all matches with pagination"""
    query = db.query(Match)
    
    if status:
        query = query.filter(Match.status == status)
    
    matches = query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()
    return matches
