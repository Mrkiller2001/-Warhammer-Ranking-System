"""
Campaign service for managing narrative campaigns.
Implements Warhammer 40K Crusade/Narrative Play rules.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import aiosqlite
from src.services.database_service import DatabaseService


@dataclass
class NarrativeOutcome:
    """Result of a narrative game."""
    attacker_won: bool
    defender_won: bool
    is_draw: bool
    attacker_req: int
    defender_req: int
    attacker_score: int
    defender_score: int
    winner_id: Optional[int] = None


class CampaignService:
    """Service for managing narrative campaigns and progression."""
    
    # Requisition Point Rules
    REQUISITION_WIN = 3
    REQUISITION_LOSS = 2
    REQUISITION_DRAW = 2
    
    # Supply Limit Rules
    STARTING_SUPPLY_LIMIT = 50
    MAX_SUPPLY_LIMIT = 100
    SUPPLY_INCREASE_PER_WIN = 5
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize campaign service.
        
        Args:
            db_service: Database service instance
        """
        self.db = db_service
    
    def calculate_narrative_outcome(
        self,
        attacker_score: int,
        defender_score: int,
        mission_type: str = "standard"
    ) -> NarrativeOutcome:
        """
        Calculate the outcome of a narrative game.
        
        Args:
            attacker_score: Victory points scored by attacker
            defender_score: Victory points scored by defender
            mission_type: Type of mission played
            
        Returns:
            NarrativeOutcome with requisition points and results
        """
        is_draw = attacker_score == defender_score
        attacker_won = attacker_score > defender_score
        defender_won = defender_score > attacker_score
        
        # Assign requisition points based on outcome
        if is_draw:
            attacker_req = self.REQUISITION_DRAW
            defender_req = self.REQUISITION_DRAW
        elif attacker_won:
            attacker_req = self.REQUISITION_WIN
            defender_req = self.REQUISITION_LOSS
        else:
            attacker_req = self.REQUISITION_LOSS
            defender_req = self.REQUISITION_WIN
        
        return NarrativeOutcome(
            attacker_won=attacker_won,
            defender_won=defender_won,
            is_draw=is_draw,
            attacker_req=attacker_req,
            defender_req=defender_req,
            attacker_score=attacker_score,
            defender_score=defender_score
        )
    
    async def record_campaign_game(
        self,
        campaign_id: int,
        planet_id: int,
        attacker_id: int,
        defender_id: int,
        attacker_score: int,
        defender_score: int,
        mission_type: str = "standard",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record a campaign game and update participant statistics.
        
        Args:
            campaign_id: Campaign ID
            planet_id: Planet where battle takes place
            attacker_id: Attacker player ID
            defender_id: Defender player ID
            attacker_score: Attacker's score
            defender_score: Defender's score
            mission_type: Mission type
            notes: Optional game notes
            
        Returns:
            Dictionary with game ID and outcome details
        """
        # Calculate narrative outcome
        outcome = self.calculate_narrative_outcome(
            attacker_score,
            defender_score,
            mission_type
        )
        
        # Determine winner ID
        winner_id = None
        if outcome.attacker_won:
            winner_id = attacker_id
        elif outcome.defender_won:
            winner_id = defender_id
        
        # Record the game in database
        game_id = await self._create_campaign_game_record(
            campaign_id=campaign_id,
            planet_id=planet_id,
            attacker_id=attacker_id,
            defender_id=defender_id,
            attacker_score=attacker_score,
            defender_score=defender_score,
            attacker_req=outcome.attacker_req,
            defender_req=outcome.defender_req,
            winner_id=winner_id,
            mission_type=mission_type,
            notes=notes
        )
        
        # Update participant statistics
        await self._update_participant_stats(
            campaign_id=campaign_id,
            player_id=attacker_id,
            requisition_gained=outcome.attacker_req,
            won=outcome.attacker_won
        )
        
        await self._update_participant_stats(
            campaign_id=campaign_id,
            player_id=defender_id,
            requisition_gained=outcome.defender_req,
            won=outcome.defender_won
        )
        
        # Update planet statistics and generate narrative
        await self._update_planet_after_battle(
            planet_id=planet_id,
            winner_id=winner_id,
            score_diff=abs(attacker_score - defender_score),
            game_id=game_id,
            campaign_id=campaign_id
        )
        
        return {
            "game_id": game_id,
            "outcome": outcome.__dict__
        }
    
    async def add_participant(
        self,
        campaign_id: int,
        player_id: int
    ) -> int:
        """
        Add a player to a campaign.
        
        Args:
            campaign_id: Campaign ID
            player_id: Player ID
            
        Returns:
            Participant ID
        """
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO campaign_participants (campaign_id, player_id)
                VALUES (?, ?)
                """,
                (campaign_id, player_id)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def get_participant_stats(
        self,
        campaign_id: int,
        player_id: int
    ) -> Optional[Dict]:
        """
        Get participant statistics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            player_id: Player ID
            
        Returns:
            Dictionary with participant stats or None
        """
        async with aiosqlite.connect(self.db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM campaign_participants
                WHERE campaign_id = ? AND player_id = ?
                """,
                (campaign_id, player_id)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def _create_campaign_game_record(
        self,
        campaign_id: int,
        planet_id: int,
        attacker_id: int,
        defender_id: int,
        attacker_score: int,
        defender_score: int,
        attacker_req: int,
        defender_req: int,
        winner_id: Optional[int],
        mission_type: str,
        notes: Optional[str]
    ) -> int:
        """Create campaign game record in database."""
        async with aiosqlite.connect(self.db.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO campaign_games (
                    campaign_id, planet_id, attacker_id, defender_id,
                    attacker_score, defender_score,
                    attacker_req, defender_req,
                    winner_id, mission_type, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id, planet_id, attacker_id, defender_id,
                    attacker_score, defender_score,
                    attacker_req, defender_req,
                    winner_id, mission_type, notes
                )
            )
            await db.commit()
            return cursor.lastrowid
    
    async def _update_participant_stats(
        self,
        campaign_id: int,
        player_id: int,
        requisition_gained: int,
        won: bool
    ) -> None:
        """Update participant statistics after a game."""
        async with aiosqlite.connect(self.db.db_path) as db:
            # Update requisition points and battle record
            if won:
                await db.execute(
                    """
                    UPDATE campaign_participants
                    SET requisition_points = requisition_points + ?,
                        battles_won = battles_won + 1,
                        supply_limit = MIN(supply_limit + ?, ?)
                    WHERE campaign_id = ? AND player_id = ?
                    """,
                    (
                        requisition_gained,
                        self.SUPPLY_INCREASE_PER_WIN,
                        self.MAX_SUPPLY_LIMIT,
                        campaign_id,
                        player_id
                    )
                )
            else:
                await db.execute(
                    """
                    UPDATE campaign_participants
                    SET requisition_points = requisition_points + ?,
                        battles_lost = battles_lost + 1
                    WHERE campaign_id = ? AND player_id = ?
                    """,
                    (requisition_gained, campaign_id, player_id)
                )
            await db.commit()
    
    async def _update_planet_after_battle(
        self,
        planet_id: int,
        winner_id: Optional[int],
        score_diff: int,
        game_id: int,
        campaign_id: int
    ) -> None:
        """Update planet after a battle and generate narrative."""
        from src.services.narrative_service import NarrativeService
        
        # Get planet info
        planet = await self.db.get_planet_by_id(planet_id)
        if not planet:
            return
        
        # Update games played
        new_games_played = planet['games_played'] + 1
        
        # Determine controller (simplified - winner of latest battle)
        controller = None
        is_contested = True
        
        if winner_id:
            # Get winner player info
            async with aiosqlite.connect(self.db.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT discord_name FROM players WHERE id = ?",
                    (winner_id,)
                )
                winner = await cursor.fetchone()
                if winner:
                    controller = winner['discord_name']
        
        # Update planet stats
        await self.db.update_planet_stats(
            planet_id=planet_id,
            games_played=new_games_played,
            is_contested=is_contested,
            current_controller=controller
        )
        
        # Generate battle narrative
        if winner_id and controller:
            narrative_service = NarrativeService()
            
            # Get loser name for narrative
            async with aiosqlite.connect(self.db.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    """
                    SELECT p.discord_name 
                    FROM campaign_games cg
                    JOIN players p ON (p.id = cg.attacker_id OR p.id = cg.defender_id)
                    WHERE cg.id = ? AND p.id != ?
                    LIMIT 1
                    """,
                    (game_id, winner_id)
                )
                loser = await cursor.fetchone()
                loser_name = loser['discord_name'] if loser else "Unknown"
            
            # Generate battle narrative
            battle_narrative = narrative_service.generate_battle_narrative(
                planet_name=planet['name'],
                planet_type=planet['planet_type'],
                winner_name=controller,
                loser_name=loser_name,
                score_diff=score_diff
            )
            
            # Create battle narrative event
            await self.db.create_narrative_event(
                campaign_id=campaign_id,
                event_type="battle",
                title=f"Battle on {planet['name']}",
                description=battle_narrative,
                planet_id=planet_id,
                game_id=game_id
            )
            
            # Check for conquest milestones
            if new_games_played in [3, 5, 8]:
                conquest_narrative = narrative_service.generate_planet_conquest_event(
                    planet_name=planet['name'],
                    controller=controller,
                    games_played=new_games_played
                )
                
                await self.db.create_narrative_event(
                    campaign_id=campaign_id,
                    event_type="conquest",
                    title=f"Control of {planet['name']}",
                    description=conquest_narrative,
                    planet_id=planet_id
                )
