"""
Game management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models import GameCreate, GameResponse
from src.services import DatabaseService
from src.dependencies import get_db_service

router = APIRouter()


@router.post("/", response_model=GameResponse, status_code=201)
async def create_game(
    game: GameCreate,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create a new game.
    
    Args:
        game: Game creation data
        db: Database service
        
    Returns:
        Created game information
    """
    # Check if game already exists
    existing = await db.get_game_by_name(game.name)
    if existing:
        raise HTTPException(status_code=400, detail="Game already exists")
    
    # Create game
    game_id = await db.create_game(game.name, game.display_name)
    
    # Retrieve and return created game
    created_game = await db.get_game_by_id(game_id)
    return GameResponse(**created_game)


@router.get("/", response_model=List[GameResponse])
async def list_games(db: DatabaseService = Depends(get_db_service)):
    """
    Get all games.
    
    Args:
        db: Database service
        
    Returns:
        List of all games
    """
    games = await db.get_all_games()
    return [GameResponse(**game) for game in games]


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a specific game by ID.
    
    Args:
        game_id: Game ID
        db: Database service
        
    Returns:
        Game information
    """
    game = await db.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameResponse(**game)


@router.get("/name/{game_name}", response_model=GameResponse)
async def get_game_by_name(
    game_name: str,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a specific game by name.
    
    Args:
        game_name: Game name
        db: Database service
        
    Returns:
        Game information
    """
    game = await db.get_game_by_name(game_name)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameResponse(**game)
