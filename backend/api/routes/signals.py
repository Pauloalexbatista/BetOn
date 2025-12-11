from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from database.database import get_db
from analysis.scanner import SignalScanner

router = APIRouter()

@router.get("/today")
def get_daily_signals(hours: int = 48, db: Session = Depends(get_db)):
    """
    Get betting signals for the next N hours (default 48).
    Uses active strategies to scan upcoming matches.
    """
    try:
        scanner = SignalScanner(db)
        signals = scanner.scan(hours_ahead=hours)
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        print(f"Error scanning signals: {e}")
        return {"signals": [], "error": str(e)}


@router.post("/clear")
def clear_signals():
    """
    Clear all signals (marks them as read).
    Note: Signals are regenerated on next scan, this is just for UI cleanup.
    Returns success message.
    """
    try:
        # Since signals are dynamically generated, we just return success
        # In future, could mark certain matches as "dismissed" in a separate table
        return {
            "status": "success",
            "message": "Signals cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
