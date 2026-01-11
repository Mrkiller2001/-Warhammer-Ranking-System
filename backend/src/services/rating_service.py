"""
Rating service implementing Glicko-2 rating system with OOP design.
"""

from glicko2 import Player
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class RatingUpdate:
    """Result of a rating update."""
    rating: float
    rating_deviation: float
    volatility: float
    rating_change: float


class RatingService:
    """Service for managing Glicko-2 rating calculations."""
    
    def __init__(self, tau: float = 0.5):
        """
        Initialize the rating service.
        
        Args:
            tau: System constant constraining volatility changes (0.3-1.2 typical, 0.5 default)
        """
        self.tau = tau
    
    def create_player(
        self,
        rating: float = 1500.0,
        rd: float = 350.0,
        vol: float = 0.06
    ) -> Player:
        """
        Create a Glicko-2 player object.
        
        Args:
            rating: Initial rating (default 1500)
            rd: Rating deviation (default 350 for new players)
            vol: Volatility (default 0.06)
            
        Returns:
            Player object
        """
        return Player(rating=rating, rd=rd, vol=vol)
    
    def calculate_match_outcome(
        self,
        winner_data: Dict[str, float],
        loser_data: Dict[str, float]
    ) -> Tuple[RatingUpdate, RatingUpdate]:
        """
        Calculate rating updates after a match.
        
        Args:
            winner_data: Dictionary with 'rating', 'rating_deviation', 'volatility' keys
            loser_data: Dictionary with 'rating', 'rating_deviation', 'volatility' keys
            
        Returns:
            Tuple of (winner_update, loser_update)
        """
        # Create player objects
        winner = self.create_player(
            winner_data['rating'],
            winner_data['rating_deviation'],
            winner_data['volatility']
        )
        
        loser = self.create_player(
            loser_data['rating'],
            loser_data['rating_deviation'],
            loser_data['volatility']
        )
        
        # Store original ratings
        winner_rating_before = winner.rating
        loser_rating_before = loser.rating
        
        # Update ratings based on match result
        winner.update_player([loser.rating], [loser.rd], [1])  # Winner scored 1 (win)
        loser.update_player([winner_rating_before], [winner.rd], [0])  # Loser scored 0 (loss)
        
        # Calculate rating changes
        winner_change = winner.rating - winner_rating_before
        loser_change = loser.rating - loser_rating_before
        
        # Create update objects
        winner_update = RatingUpdate(
            rating=winner.rating,
            rating_deviation=winner.rd,
            volatility=winner.vol,
            rating_change=winner_change
        )
        
        loser_update = RatingUpdate(
            rating=loser.rating,
            rating_deviation=loser.rd,
            volatility=loser.vol,
            rating_change=loser_change
        )
        
        return winner_update, loser_update
    
    def get_expected_score(
        self,
        player_rating: float,
        opponent_rating: float,
        opponent_rd: float
    ) -> float:
        """
        Calculate expected score (win probability) for a player.
        
        Args:
            player_rating: Player's current rating
            opponent_rating: Opponent's current rating
            opponent_rd: Opponent's rating deviation
            
        Returns:
            Expected score (0-1, where 0.5 = 50% win probability)
        """
        player = self.create_player(rating=player_rating)
        return player._E(opponent_rating, opponent_rd)
    
    def get_win_probability(
        self,
        player_rating: float,
        opponent_rating: float,
        opponent_rd: float = 350.0
    ) -> float:
        """
        Calculate win probability percentage.
        
        Args:
            player_rating: Player's current rating
            opponent_rating: Opponent's current rating
            opponent_rd: Opponent's rating deviation (default 350)
            
        Returns:
            Win probability as a percentage (0-100)
        """
        expected_score = self.get_expected_score(
            player_rating,
            opponent_rating,
            opponent_rd
        )
        return expected_score * 100
