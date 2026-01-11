"""
Data models for the application using Pydantic.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# Player Models
class PlayerBase(BaseModel):
    """Base player model."""
    discord_id: str = Field(..., description="Discord user ID")
    discord_name: str = Field(..., description="Discord username")


class PlayerCreate(PlayerBase):
    """Model for creating a new player."""
    game_id: int = Field(..., description="Game ID the player is joining")


class PlayerUpdate(BaseModel):
    """Model for updating player information."""
    discord_name: Optional[str] = None


class PlayerRating(BaseModel):
    """Player rating information."""
    rating: float = Field(default=1500.0, description="Glicko-2 rating")
    rating_deviation: float = Field(default=350.0, description="Rating deviation (uncertainty)")
    volatility: float = Field(default=0.06, description="Rating volatility")


class PlayerStats(BaseModel):
    """Player statistics."""
    matches_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100


class PlayerResponse(PlayerBase):
    """Complete player information response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    game_id: int
    rating: float
    rating_deviation: float
    volatility: float
    matches_played: int
    wins: int
    losses: int
    last_match_date: Optional[datetime] = None
    created_at: datetime


# Game Models
class GameBase(BaseModel):
    """Base game model."""
    name: str = Field(..., description="Internal game name (lowercase, no spaces)")
    display_name: str = Field(..., description="Display name for the game")


class GameCreate(GameBase):
    """Model for creating a new game."""
    pass


class GameResponse(GameBase):
    """Complete game information response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# Match Models
class MatchCreate(BaseModel):
    """Model for creating a new match."""
    game_id: int = Field(..., description="Game ID")
    winner_discord_id: str = Field(..., description="Winner's Discord ID")
    loser_discord_id: str = Field(..., description="Loser's Discord ID")
    winner_score: Optional[int] = Field(None, description="Winner's score (optional)")
    loser_score: Optional[int] = Field(None, description="Loser's score (optional)")
    notes: Optional[str] = Field(None, description="Match notes")


class MatchResponse(BaseModel):
    """Match information response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    game_id: int
    winner_id: int
    loser_id: int
    winner_score: Optional[int]
    loser_score: Optional[int]
    notes: Optional[str]
    played_at: datetime


# Campaign Models
class CampaignBase(BaseModel):
    """Base campaign model."""
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    game_id: int = Field(..., description="Game ID")


class CampaignCreate(CampaignBase):
    """Model for creating a new campaign."""
    pass


class CampaignUpdate(BaseModel):
    """Model for updating a campaign."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CampaignResponse(CampaignBase):
    """Complete campaign information response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime]


# Campaign Game Models
class CampaignGameCreate(BaseModel):
    """Model for recording a campaign game."""
    campaign_id: int = Field(..., description="Campaign ID")
    attacker_discord_id: str = Field(..., description="Attacker's Discord ID")
    defender_discord_id: str = Field(..., description="Defender's Discord ID")
    attacker_score: int = Field(..., ge=0, description="Attacker's score")
    defender_score: int = Field(..., ge=0, description="Defender's score")
    mission_type: str = Field(default="standard", description="Mission type")
    notes: Optional[str] = Field(None, description="Game notes")


class CampaignGameResponse(BaseModel):
    """Campaign game information response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    campaign_id: int
    attacker_id: int
    defender_id: int
    attacker_score: int
    defender_score: int
    attacker_req: int
    defender_req: int
    winner_id: Optional[int]
    mission_type: str
    notes: Optional[str]
    played_at: datetime


# Ranking Models
class RankingEntry(BaseModel):
    """Single ranking entry."""
    rank: int
    discord_id: str
    discord_name: str
    rating: float
    rating_deviation: float
    matches_played: int
    wins: int
    losses: int
    win_rate: float


class RankingsResponse(BaseModel):
    """Rankings response with metadata."""
    game_id: int
    game_name: str
    rankings: list[RankingEntry]
    total_players: int
    generated_at: datetime = Field(default_factory=datetime.now)
