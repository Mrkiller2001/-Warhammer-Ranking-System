"""
Player management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models import PlayerCreate, PlayerResponse, PlayerUpdate
from src.services import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=201)
async def create_player(
    player: PlayerCreate,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create a new player for a game.
    
    Args:
        player: Player creation data
        db: Database service
        
    Returns:
        Created player information
    """
    # Check if game exists
    game = await db.get_game_by_id(player.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if player already exists for this game
    existing = await db.get_player_by_discord_id(player.discord_id, player.game_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Player already registered for this game"
        )
    
    # Create player
    player_id = await db.create_player(
        player.discord_id,
        player.discord_name,
        player.game_id
    )
    
    # Retrieve and return created player
    created_player = await db.get_player_by_id(player_id)
    return PlayerResponse(**created_player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a specific player by ID.
    
    Args:
        player_id: Player ID
        db: Database service
        
    Returns:
        Player information
    """
    player = await db.get_player_by_id(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse(**player)


@router.get("/discord/{discord_id}/game/{game_id}", response_model=PlayerResponse)
async def get_player_by_discord_id(
    discord_id: str,
    game_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a player by Discord ID and game.
    
    Args:
        discord_id: Discord user ID
        game_id: Game ID
        db: Database service
        
    Returns:
        Player information
    """
    player = await db.get_player_by_discord_id(discord_id, game_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return PlayerResponse(**player)


@router.get("/game/{game_id}", response_model=List[PlayerResponse])
async def list_players_by_game(
    game_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get all players for a specific game.
    
    Args:
        game_id: Game ID
        db: Database service
        
    Returns:
        List of players
    """
    # Check if game exists
    game = await db.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    players = await db.get_players_by_game(game_id)
    return [PlayerResponse(**player) for player in players]
