from fastapi import APIRouter

router = APIRouter()

# Import sub-routers
from api.routes import matches, bets, strategies, bankroll, analysis

# Include all route modules
router.include_router(matches.router, prefix="/matches", tags=["matches"])
router.include_router(bets.router, prefix="/bets", tags=["bets"])
router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
router.include_router(bankroll.router, prefix="/bankroll", tags=["bankroll"])
router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
