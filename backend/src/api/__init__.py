"""
API routes package initialization.
"""

from fastapi import APIRouter
from src.api.games import router as games_router
from src.api.players import router as players_router
from src.api.matches import router as matches_router
from src.api.campaigns import router as campaigns_router
from src.api.rankings import router as rankings_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(games_router, prefix="/games", tags=["games"])
api_router.include_router(players_router, prefix="/players", tags=["players"])
api_router.include_router(matches_router, prefix="/matches", tags=["matches"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(rankings_router, prefix="/rankings", tags=["rankings"])

__all__ = ["api_router"]
