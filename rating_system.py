"""
Glicko-2 rating system implementation.
Wrapper around the glicko2 library with game-specific adaptations.
"""

from glicko2 import Player


class RatingSystem:
    """Manages Glicko-2 rating calculations."""
    
    def __init__(self, tau: float = 0.5):
        """
        Initialize the rating system.
        
        Args:
            tau: System constant constraining volatility changes (0.3-1.2 typical, 0.5 default)
        """
        self.tau = tau

    def create_player(self, rating: float = 1500.0, rd: float = 350.0, vol: float = 0.06) -> Player:
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

    def update_ratings(self, winner: dict, loser: dict) -> tuple[dict, dict]:
        """
        Update ratings after a match.
        
        Args:
            winner: Dictionary with 'rating', 'rating_deviation', 'volatility' keys
            loser: Dictionary with 'rating', 'rating_deviation', 'volatility' keys
            
        Returns:
            Tuple of (updated_winner_dict, updated_loser_dict)
        """
        # Create player objects
        winner_player = self.create_player(
            winner['rating'],
            winner['rating_deviation'],
            winner['volatility']
        )
        loser_player = self.create_player(
            loser['rating'],
            loser['rating_deviation'],
            loser['volatility']
        )

        # Update ratings (1 = win, 0 = loss)
        winner_player.update_player([loser_player.rating], [loser_player.rd], [1], self.tau)
        loser_player.update_player([winner_player.rating], [winner_player.rd], [0], self.tau)

        # Return updated values
        updated_winner = {
            'rating': winner_player.rating,
            'rating_deviation': winner_player.rd,
            'volatility': winner_player.vol
        }
        updated_loser = {
            'rating': loser_player.rating,
            'rating_deviation': loser_player.rd,
            'volatility': loser_player.vol
        }

        return updated_winner, updated_loser

    def calculate_win_probability(self, player1_rating: float, player1_rd: float,
                                  player2_rating: float, player2_rd: float) -> float:
        """
        Calculate the probability that player1 beats player2.
        
        Args:
            player1_rating: Player 1's rating
            player1_rd: Player 1's rating deviation
            player2_rating: Player 2's rating
            player2_rd: Player 2's rating deviation
            
        Returns:
            Probability (0.0 to 1.0) that player1 wins
        """
        import math
        
        # Convert to Glicko-2 scale
        q = math.log(10) / 400
        g_rd2 = 1 / math.sqrt(1 + 3 * q**2 * player2_rd**2 / math.pi**2)
        
        # Calculate expected score
        exponent = -g_rd2 * (player1_rating - player2_rating) / 400
        expected = 1 / (1 + 10**exponent)
        
        return expected

    def get_rating_class(self, rating: float) -> str:
        """
        Get a human-readable rating class based on rating value.
        
        Args:
            rating: Player's rating
            
        Returns:
            Rating class string
        """
        if rating >= 2400:
            return "Legendary"
        elif rating >= 2200:
            return "Master"
        elif rating >= 2000:
            return "Expert"
        elif rating >= 1800:
            return "Advanced"
        elif rating >= 1600:
            return "Intermediate"
        elif rating >= 1400:
            return "Novice"
        else:
            return "Beginner"

    def format_rating(self, rating: float, rd: float) -> str:
        """
        Format rating with deviation for display.
        
        Args:
            rating: Player's rating
            rd: Rating deviation
            
        Returns:
            Formatted string like "1650 ± 45"
        """
        return f"{int(rating)} ± {int(rd)}"
