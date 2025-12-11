from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import analysis, bankroll, strategies, signals, matches, bets, system, pareto_teams
from database.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    logger.info("Starting BetOn API...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down BetOn API...")


app = FastAPI(
    title="BetOn API",
    description="Sistema de automação de apostas desportivas",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(pareto_teams.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(bankroll.router, prefix="/api/bankroll", tags=["Bankroll"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(bets.router, prefix="/api/bets", tags=["Bets"])
app.include_router(system.router, prefix="/api/system", tags=["System"])


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.get("/test-route")
def test_route():
    return {"message": "I am alive and updated"}



# Force Reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
