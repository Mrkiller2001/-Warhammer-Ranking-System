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
    CampaignGameResponse,
    PlanetResponse,
    NarrativeEventResponse
)
from src.services import DatabaseService, CampaignService
from src.services.narrative_service import NarrativeService
from src.dependencies import get_db_service, get_campaign_service

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    campaign: CampaignCreate,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create a new campaign with procedurally generated solar system.
    
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
    
    # Generate unique solar system and narrative
    narrative_service = NarrativeService()
    planets_data, opening_narrative, seed = narrative_service.generate_solar_system(
        campaign.name,
        0  # Temporary ID, will use real one after creation
    )
    
    # Create campaign
    campaign_id = await db.create_campaign(
        campaign.name,
        campaign.game_id,
        seed,
        campaign.description
    )
    
    # Create planets for the campaign
    for planet_data in planets_data:
        await db.create_planet(
            campaign_id=campaign_id,
            name=planet_data['name'],
            planet_type=planet_data['planet_type'],
            position=planet_data['position'],
            color=planet_data['color'],
            size=planet_data['size'],
            description=planet_data['description'],
            strategic_value=planet_data['strategic_value']
        )
    
    # Create opening narrative event
    await db.create_narrative_event(
        campaign_id=campaign_id,
        event_type="campaign_start",
        title=f"The {campaign.name} Begins",
        description=opening_narrative
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
    
    # Verify planet exists
    planet = await db.get_planet_by_id(game.planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    
    # Record campaign game
    result = await campaign_service.record_campaign_game(
        campaign_id=game.campaign_id,
        planet_id=game.planet_id,
        attacker_id=attacker['id'],
        defender_id=defender['id'],
        attacker_score=game.attacker_score,
        defender_score=game.defender_score,
        mission_type=game.mission_type,
        notes=game.notes
    )
    
    return result


@router.get("/{campaign_id}/planets", response_model=List[PlanetResponse])
async def get_campaign_planets(
    campaign_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get all planets in a campaign.
    
    Args:
        campaign_id: Campaign ID
        db: Database service
        
    Returns:
        List of planets in the campaign
    """
    campaign = await db.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    planets = await db.get_planets_by_campaign(campaign_id)
    return [PlanetResponse(**planet) for planet in planets]


@router.get("/{campaign_id}/narrative", response_model=List[NarrativeEventResponse])
async def get_campaign_narrative(
    campaign_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get narrative events for a campaign.
    
    Args:
        campaign_id: Campaign ID
        db: Database service
        
    Returns:
        List of narrative events
    """
    campaign = await db.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    events = await db.get_narrative_events_by_campaign(campaign_id)
    return [NarrativeEventResponse(**event) for event in events]


@router.get("/planets/{planet_id}/games", response_model=List[CampaignGameResponse])
async def get_planet_games(
    planet_id: int,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get all games that have taken place on a specific planet.
    
    Args:
        planet_id: Planet ID
        db: Database service
        
    Returns:
        List of campaign games on the planet
    """
    planet = await db.get_planet_by_id(planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    
    games = await db.get_campaign_games_by_planet(planet_id)
    return [CampaignGameResponse(**game) for game in games]
