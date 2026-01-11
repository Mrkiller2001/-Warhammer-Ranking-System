"""
Rankings API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from src.models import RankingsResponse, RankingEntry
from src.services import DatabaseService
from src.dependencies import get_db_service
from datetime import datetime

router = APIRouter()


@router.get("/game/{game_id}", response_model=RankingsResponse)
async def get_game_rankings(
    game_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get rankings for a specific game.
    
    Args:
        game_id: Game ID
        db: Database service
        
    Returns:
        Rankings with player statistics
    """
    # Check if game exists
    game = await db.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get all players for the game (already sorted by rating)
    players = await db.get_players_by_game(game_id)
    
    # Create ranking entries
    rankings = []
    for rank, player in enumerate(players, start=1):
        win_rate = 0.0
        if player['matches_played'] > 0:
            win_rate = (player['wins'] / player['matches_played']) * 100
        
        rankings.append(
            RankingEntry(
                rank=rank,
                discord_id=player['discord_id'],
                discord_name=player['discord_name'],
                rating=player['rating'],
                rating_deviation=player['rating_deviation'],
                matches_played=player['matches_played'],
                wins=player['wins'],
                losses=player['losses'],
                win_rate=round(win_rate, 2)
            )
        )
    
    return RankingsResponse(
        game_id=game_id,
        game_name=game['display_name'],
        rankings=rankings,
        total_players=len(rankings),
        generated_at=datetime.now()
    )
