"""
Campaign management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CampaignGameCreate,
    CampaignGameResponse
)
from src.services import DatabaseService, CampaignService
from src.dependencies import get_db_service, get_campaign_service

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create a new campaign.
    
    Args:
        campaign: Campaign creation data
        db: Database service
        
    Returns:
        Created campaign information
    """
    # Check if game exists
    game = await db.get_game_by_id(campaign.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Create campaign
    campaign_id = await db.create_campaign(
        campaign.name,
        campaign.game_id,
        campaign.description
    )
    
    # Retrieve and return created campaign
    created_campaign = await db.get_campaign_by_id(campaign_id)
    return CampaignResponse(**created_campaign)


@router.get("/active", response_model=List[CampaignResponse])
async def list_active_campaigns(db: DatabaseService = Depends(get_db_service)):
    """
    Get all active campaigns.
    
    Args:
        db: Database service
        
    Returns:
        List of active campaigns
    """
    campaigns = await db.get_active_campaigns()
    return [CampaignResponse(**campaign) for campaign in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a specific campaign by ID.
    
    Args:
        campaign_id: Campaign ID
        db: Database service
        
    Returns:
        Campaign information
    """
    campaign = await db.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse(**campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Update a campaign.
    
    Args:
        campaign_id: Campaign ID
        campaign_update: Updated campaign data
        db: Database service
        
    Returns:
        Updated campaign information
    """
    # Check if campaign exists
    campaign = await db.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update campaign
    await db.update_campaign(
        campaign_id,
        name=campaign_update.name,
        description=campaign_update.description,
        is_active=campaign_update.is_active
    )
    
    # Retrieve and return updated campaign
    updated_campaign = await db.get_campaign_by_id(campaign_id)
    return CampaignResponse(**updated_campaign)


@router.post("/games", response_model=dict, status_code=201)
async def record_campaign_game(
    game: CampaignGameCreate,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Record a campaign game.
    
    Args:
        game: Campaign game data
        campaign_service: Campaign service
        db: Database service
        
    Returns:
        Game outcome and requisition points
    """
    # Get players
    attacker = await db.get_player_by_discord_id(
        game.attacker_discord_id,
        (await db.get_campaign_by_id(game.campaign_id))['game_id']
    )
    defender = await db.get_player_by_discord_id(
        game.defender_discord_id,
        (await db.get_campaign_by_id(game.campaign_id))['game_id']
    )
    
    if not attacker:
        raise HTTPException(status_code=404, detail="Attacker not found")
    if not defender:
        raise HTTPException(status_code=404, detail="Defender not found")
    
    # Record campaign game
    result = await campaign_service.record_campaign_game(
        campaign_id=game.campaign_id,
        attacker_id=attacker['id'],
        defender_id=defender['id'],
        attacker_score=game.attacker_score,
        defender_score=game.defender_score,
        mission_type=game.mission_type,
        notes=game.notes
    )
    
    return result
