"""
Match recording API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models import MatchCreate, MatchResponse
from src.services import DatabaseService, RatingService
from src.dependencies import get_db_service, get_rating_service

router = APIRouter()


@router.post("/", response_model=MatchResponse, status_code=201)
async def record_match(
    match: MatchCreate,
    db: DatabaseService = Depends(get_db_service),
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Record a new match and update player ratings.
    
    Args:
        match: Match data
        db: Database service
        rating_service: Rating service
        
    Returns:
        Created match information
    """
    # Get winner and loser players
    winner = await db.get_player_by_discord_id(match.winner_discord_id, match.game_id)
    loser = await db.get_player_by_discord_id(match.loser_discord_id, match.game_id)
    
    if not winner:
        raise HTTPException(status_code=404, detail="Winner not found")
    if not loser:
        raise HTTPException(status_code=404, detail="Loser not found")
    
    # Calculate new ratings
    winner_update, loser_update = rating_service.calculate_match_outcome(
        {
            'rating': winner['rating'],
            'rating_deviation': winner['rating_deviation'],
            'volatility': winner['volatility']
        },
        {
            'rating': loser['rating'],
            'rating_deviation': loser['rating_deviation'],
            'volatility': loser['volatility']
        }
    )
    
    # Create match record
    match_id = await db.create_match(
        game_id=match.game_id,
        winner_id=winner['id'],
        loser_id=loser['id'],
        winner_rating_before=winner['rating'],
        loser_rating_before=loser['rating'],
        winner_rating_after=winner_update.rating,
        loser_rating_after=loser_update.rating,
        winner_score=match.winner_score,
        loser_score=match.loser_score,
        notes=match.notes
    )
    
    # Update player ratings
    await db.update_player_rating(
        winner['id'],
        winner_update.rating,
        winner_update.rating_deviation,
        winner_update.volatility
    )
    await db.update_player_rating(
        loser['id'],
        loser_update.rating,
        loser_update.rating_deviation,
        loser_update.volatility
    )
    
    # Update player statistics
    await db.update_player_stats(winner['id'], won=True)
    await db.update_player_stats(loser['id'], won=False)
    
    # Retrieve and return created match
    # Note: For simplicity, returning a constructed response
    return MatchResponse(
        id=match_id,
        game_id=match.game_id,
        winner_id=winner['id'],
        loser_id=loser['id'],
        winner_score=match.winner_score,
        loser_score=match.loser_score,
        notes=match.notes,
        played_at=None  # Will be set by database default
    )


@router.get("/game/{game_id}", response_model=List[MatchResponse])
async def list_matches_by_game(
    game_id: int,
    limit: int = 50,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get recent matches for a game.
    
    Args:
        game_id: Game ID
        limit: Maximum number of matches to return
        db: Database service
        
    Returns:
        List of matches
    """
    # Check if game exists
    game = await db.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    matches = await db.get_matches_by_game(game_id, limit)
    return [MatchResponse(**match) for match in matches]
