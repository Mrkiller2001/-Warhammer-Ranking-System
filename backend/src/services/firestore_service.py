"""
Firebase Firestore database service layer.
Replaces SQLite/PostgreSQL with Firestore.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter
from src.config import settings


class FirestoreService:
    """Database service using Firebase Firestore."""
    
    def __init__(self):
        """Initialize Firestore service."""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            if settings.firebase_credentials_path:
                cred = credentials.Certificate(settings.firebase_credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for deployed environment)
                firebase_admin.initialize_app()
        
        self.db = firestore.client()
    
    async def initialize(self) -> None:
        """Initialize Firestore collections (no schema needed)."""
        # Firestore is schemaless, but we can create initial indexes if needed
        # Indexes are defined in firestore.indexes.json
        pass
    
    # ==================== GAMES ====================
    
    async def create_game(self, name: str, display_name: str) -> Dict[str, Any]:
        """Create a new game."""
        game_ref = self.db.collection('games').document()
        game_data = {
            'name': name,
            'display_name': display_name,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        game_ref.set(game_data)
        
        # Get the created document
        game_doc = game_ref.get()
        return {'id': game_doc.id, **game_doc.to_dict()}
    
    async def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get a game by ID."""
        game_ref = self.db.collection('games').document(game_id)
        game_doc = game_ref.get()
        
        if game_doc.exists:
            return {'id': game_doc.id, **game_doc.to_dict()}
        return None
    
    async def get_game_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a game by name."""
        games_ref = self.db.collection('games')
        query = games_ref.where(filter=FieldFilter('name', '==', name)).limit(1)
        results = query.stream()
        
        for doc in results:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    async def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all games."""
        games_ref = self.db.collection('games')
        games = []
        
        for doc in games_ref.stream():
            games.append({'id': doc.id, **doc.to_dict()})
        
        return games
    
    # ==================== PLAYERS ====================
    
    async def create_player(
        self,
        discord_id: str,
        discord_name: str,
        game_id: str,
        rating: float = 1500.0,
        rating_deviation: float = 350.0,
        volatility: float = 0.06
    ) -> Dict[str, Any]:
        """Create a new player."""
        player_ref = self.db.collection('players').document()
        player_data = {
            'discord_id': discord_id,
            'discord_name': discord_name,
            'game_id': game_id,
            'rating': rating,
            'rating_deviation': rating_deviation,
            'volatility': volatility,
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'last_match_date': None,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        player_ref.set(player_data)
        
        player_doc = player_ref.get()
        return {'id': player_doc.id, **player_doc.to_dict()}
    
    async def get_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get a player by ID."""
        player_ref = self.db.collection('players').document(player_id)
        player_doc = player_ref.get()
        
        if player_doc.exists:
            return {'id': player_doc.id, **player_doc.to_dict()}
        return None
    
    async def get_player_by_discord_and_game(
        self,
        discord_id: str,
        game_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a player by Discord ID and game."""
        players_ref = self.db.collection('players')
        query = players_ref.where(filter=FieldFilter('discord_id', '==', discord_id))\
                          .where(filter=FieldFilter('game_id', '==', game_id))\
                          .limit(1)
        
        for doc in query.stream():
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    async def get_players_by_game(self, game_id: str) -> List[Dict[str, Any]]:
        """Get all players for a game, sorted by rating."""
        players_ref = self.db.collection('players')
        query = players_ref.where(filter=FieldFilter('game_id', '==', game_id))\
                          .order_by('rating', direction=firestore.Query.DESCENDING)
        
        players = []
        for doc in query.stream():
            players.append({'id': doc.id, **doc.to_dict()})
        
        return players
    
    async def update_player(
        self,
        player_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update player information."""
        player_ref = self.db.collection('players').document(player_id)
        player_ref.update(updates)
        
        player_doc = player_ref.get()
        if player_doc.exists:
            return {'id': player_doc.id, **player_doc.to_dict()}
        return None
    
    async def update_player_rating(
        self,
        player_id: str,
        rating: float,
        rating_deviation: float,
        volatility: float
    ) -> None:
        """Update player's rating."""
        player_ref = self.db.collection('players').document(player_id)
        player_ref.update({
            'rating': rating,
            'rating_deviation': rating_deviation,
            'volatility': volatility
        })
    
    async def update_player_stats(
        self,
        player_id: str,
        matches_played: int,
        wins: int,
        losses: int,
        last_match_date: datetime
    ) -> None:
        """Update player's match statistics."""
        player_ref = self.db.collection('players').document(player_id)
        player_ref.update({
            'matches_played': matches_played,
            'wins': wins,
            'losses': losses,
            'last_match_date': last_match_date
        })
    
    # ==================== MATCHES ====================
    
    async def create_match(
        self,
        game_id: str,
        winner_id: str,
        loser_id: str,
        winner_score: Optional[int],
        loser_score: Optional[int],
        winner_rating_before: float,
        loser_rating_before: float,
        winner_rating_after: float,
        loser_rating_after: float,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new match record."""
        match_ref = self.db.collection('matches').document()
        match_data = {
            'game_id': game_id,
            'winner_id': winner_id,
            'loser_id': loser_id,
            'winner_score': winner_score,
            'loser_score': loser_score,
            'winner_rating_before': winner_rating_before,
            'loser_rating_before': loser_rating_before,
            'winner_rating_after': winner_rating_after,
            'loser_rating_after': loser_rating_after,
            'notes': notes,
            'played_at': firestore.SERVER_TIMESTAMP
        }
        match_ref.set(match_data)
        
        match_doc = match_ref.get()
        return {'id': match_doc.id, **match_doc.to_dict()}
    
    async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get a match by ID."""
        match_ref = self.db.collection('matches').document(match_id)
        match_doc = match_ref.get()
        
        if match_doc.exists:
            return {'id': match_doc.id, **match_doc.to_dict()}
        return None
    
    async def get_matches_by_game(
        self,
        game_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent matches for a game."""
        matches_ref = self.db.collection('matches')
        query = matches_ref.where(filter=FieldFilter('game_id', '==', game_id))\
                          .order_by('played_at', direction=firestore.Query.DESCENDING)\
                          .limit(limit)
        
        matches = []
        for doc in query.stream():
            matches.append({'id': doc.id, **doc.to_dict()})
        
        return matches
    
    async def get_matches_by_player(
        self,
        player_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get matches for a specific player."""
        matches_ref = self.db.collection('matches')
        
        # Get matches where player was winner
        winner_query = matches_ref.where(filter=FieldFilter('winner_id', '==', player_id))\
                                  .order_by('played_at', direction=firestore.Query.DESCENDING)\
                                  .limit(limit)
        
        # Get matches where player was loser
        loser_query = matches_ref.where(filter=FieldFilter('loser_id', '==', player_id))\
                                .order_by('played_at', direction=firestore.Query.DESCENDING)\
                                .limit(limit)
        
        matches = []
        for doc in winner_query.stream():
            matches.append({'id': doc.id, **doc.to_dict()})
        
        for doc in loser_query.stream():
            match_data = {'id': doc.id, **doc.to_dict()}
            if match_data not in matches:
                matches.append(match_data)
        
        # Sort by played_at
        matches.sort(key=lambda x: x.get('played_at', datetime.min), reverse=True)
        return matches[:limit]
    
    # ==================== CAMPAIGNS ====================
    
    async def create_campaign(
        self,
        name: str,
        description: str,
        game_id: str,
        narrative_seed: int
    ) -> Dict[str, Any]:
        """Create a new campaign."""
        campaign_ref = self.db.collection('campaigns').document()
        campaign_data = {
            'name': name,
            'description': description,
            'game_id': game_id,
            'narrative_seed': narrative_seed,
            'is_active': True,
            'created_at': firestore.SERVER_TIMESTAMP,
            'ended_at': None
        }
        campaign_ref.set(campaign_data)
        
        campaign_doc = campaign_ref.get()
        return {'id': campaign_doc.id, **campaign_doc.to_dict()}
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by ID."""
        campaign_ref = self.db.collection('campaigns').document(campaign_id)
        campaign_doc = campaign_ref.get()
        
        if campaign_doc.exists:
            return {'id': campaign_doc.id, **campaign_doc.to_dict()}
        return None
    
    async def get_campaigns_by_game(
        self,
        game_id: str,
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get campaigns for a game."""
        campaigns_ref = self.db.collection('campaigns')
        query = campaigns_ref.where(filter=FieldFilter('game_id', '==', game_id))
        
        if active_only:
            query = query.where(filter=FieldFilter('is_active', '==', True))
        
        campaigns = []
        for doc in query.stream():
            campaigns.append({'id': doc.id, **doc.to_dict()})
        
        return campaigns
    
    async def update_campaign(
        self,
        campaign_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update campaign information."""
        campaign_ref = self.db.collection('campaigns').document(campaign_id)
        campaign_ref.update(updates)
        
        campaign_doc = campaign_ref.get()
        if campaign_doc.exists:
            return {'id': campaign_doc.id, **campaign_doc.to_dict()}
        return None
    
    async def end_campaign(self, campaign_id: str) -> None:
        """Mark a campaign as ended."""
        campaign_ref = self.db.collection('campaigns').document(campaign_id)
        campaign_ref.update({
            'is_active': False,
            'ended_at': firestore.SERVER_TIMESTAMP
        })
    
    # ==================== CAMPAIGN GAMES ====================
    
    async def create_campaign_game(
        self,
        campaign_id: str,
        planet_id: str,
        attacker_id: str,
        defender_id: str,
        attacker_score: int,
        defender_score: int,
        attacker_req: int,
        defender_req: int,
        winner_id: Optional[str],
        mission_type: str = 'standard',
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a campaign game record."""
        game_ref = self.db.collection('campaigns').document(campaign_id)\
                         .collection('games').document()
        game_data = {
            'planet_id': planet_id,
            'attacker_id': attacker_id,
            'defender_id': defender_id,
            'attacker_score': attacker_score,
            'defender_score': defender_score,
            'attacker_req': attacker_req,
            'defender_req': defender_req,
            'winner_id': winner_id,
            'mission_type': mission_type,
            'notes': notes,
            'played_at': firestore.SERVER_TIMESTAMP
        }
        game_ref.set(game_data)
        
        game_doc = game_ref.get()
        return {'id': game_doc.id, **game_doc.to_dict()}
    
    async def get_campaign_games(
        self,
        campaign_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get games for a campaign."""
        games_ref = self.db.collection('campaigns').document(campaign_id)\
                          .collection('games')\
                          .order_by('played_at', direction=firestore.Query.DESCENDING)\
                          .limit(limit)
        
        games = []
        for doc in games_ref.stream():
            games.append({'id': doc.id, **doc.to_dict()})
        
        return games
    
    async def get_campaign_games_by_planet(
        self,
        campaign_id: str,
        planet_id: str
    ) -> List[Dict[str, Any]]:
        """Get all games for a specific planet."""
        games_ref = self.db.collection('campaigns').document(campaign_id)\
                          .collection('games')\
                          .where(filter=FieldFilter('planet_id', '==', planet_id))
        
        games = []
        for doc in games_ref.stream():
            games.append({'id': doc.id, **doc.to_dict()})
        
        return games
    
    # ==================== CAMPAIGN PARTICIPANTS ====================
    
    async def create_campaign_participant(
        self,
        campaign_id: str,
        player_id: str,
        requisition_points: int = 0,
        supply_limit: int = 50
    ) -> Dict[str, Any]:
        """Add a participant to a campaign."""
        participant_ref = self.db.collection('campaigns').document(campaign_id)\
                                .collection('participants').document()
        participant_data = {
            'player_id': player_id,
            'requisition_points': requisition_points,
            'supply_limit': supply_limit,
            'battles_won': 0,
            'battles_lost': 0,
            'joined_at': firestore.SERVER_TIMESTAMP
        }
        participant_ref.set(participant_data)
        
        participant_doc = participant_ref.get()
        return {'id': participant_doc.id, **participant_doc.to_dict()}
    
    async def get_campaign_participants(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """Get all participants in a campaign."""
        participants_ref = self.db.collection('campaigns').document(campaign_id)\
                                 .collection('participants')
        
        participants = []
        for doc in participants_ref.stream():
            participants.append({'id': doc.id, **doc.to_dict()})
        
        return participants
    
    async def get_campaign_participant(
        self,
        campaign_id: str,
        player_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific participant in a campaign."""
        participants_ref = self.db.collection('campaigns').document(campaign_id)\
                                 .collection('participants')
        query = participants_ref.where(filter=FieldFilter('player_id', '==', player_id)).limit(1)
        
        for doc in query.stream():
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    async def update_campaign_participant(
        self,
        campaign_id: str,
        participant_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update campaign participant information."""
        participant_ref = self.db.collection('campaigns').document(campaign_id)\
                                .collection('participants').document(participant_id)
        participant_ref.update(updates)
        
        participant_doc = participant_ref.get()
        if participant_doc.exists:
            return {'id': participant_doc.id, **participant_doc.to_dict()}
        return None
    
    # ==================== PLANETS ====================
    
    async def create_planet(
        self,
        campaign_id: str,
        name: str,
        planet_type: str,
        description: str,
        position: int,
        size: float,
        color: str,
        strategic_value: int
    ) -> Dict[str, Any]:
        """Create a planet for a campaign."""
        planet_ref = self.db.collection('campaigns').document(campaign_id)\
                           .collection('planets').document()
        planet_data = {
            'name': name,
            'planet_type': planet_type,
            'description': description,
            'position': position,
            'size': size,
            'color': color,
            'strategic_value': strategic_value,
            'current_controller': None,
            'is_contested': False,
            'games_played': 0,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        planet_ref.set(planet_data)
        
        planet_doc = planet_ref.get()
        return {'id': planet_doc.id, **planet_doc.to_dict()}
    
    async def get_campaign_planets(
        self,
        campaign_id: str
    ) -> List[Dict[str, Any]]:
        """Get all planets in a campaign."""
        planets_ref = self.db.collection('campaigns').document(campaign_id)\
                            .collection('planets')\
                            .order_by('position')
        
        planets = []
        for doc in planets_ref.stream():
            planets.append({'id': doc.id, **doc.to_dict()})
        
        return planets
    
    async def get_planet(
        self,
        campaign_id: str,
        planet_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific planet."""
        planet_ref = self.db.collection('campaigns').document(campaign_id)\
                           .collection('planets').document(planet_id)
        planet_doc = planet_ref.get()
        
        if planet_doc.exists:
            return {'id': planet_doc.id, **planet_doc.to_dict()}
        return None
    
    async def update_planet(
        self,
        campaign_id: str,
        planet_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update planet information."""
        planet_ref = self.db.collection('campaigns').document(campaign_id)\
                           .collection('planets').document(planet_id)
        planet_ref.update(updates)
        
        planet_doc = planet_ref.get()
        if planet_doc.exists:
            return {'id': planet_doc.id, **planet_doc.to_dict()}
        return None
    
    # ==================== NARRATIVE EVENTS ====================
    
    async def create_narrative_event(
        self,
        campaign_id: str,
        event_type: str,
        title: str,
        description: str,
        planet_id: Optional[str] = None,
        player_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a narrative event for a campaign."""
        event_ref = self.db.collection('campaigns').document(campaign_id)\
                          .collection('events').document()
        event_data = {
            'event_type': event_type,
            'title': title,
            'description': description,
            'planet_id': planet_id,
            'player_id': player_id,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        event_ref.set(event_data)
        
        event_doc = event_ref.get()
        return {'id': event_doc.id, **event_doc.to_dict()}
    
    async def get_campaign_events(
        self,
        campaign_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get narrative events for a campaign."""
        events_ref = self.db.collection('campaigns').document(campaign_id)\
                           .collection('events')\
                           .order_by('created_at', direction=firestore.Query.DESCENDING)\
                           .limit(limit)
        
        events = []
        for doc in events_ref.stream():
            events.append({'id': doc.id, **doc.to_dict()})
        
        return events


# Create singleton instance
firestore_service = FirestoreService()
