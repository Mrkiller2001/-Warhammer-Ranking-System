"""
Dependency injection for FastAPI routes.
"""

from src.services import FirestoreService, RatingService, CampaignService
from src.config import settings

# Service instances (singleton pattern)
_db_service: FirestoreService = None
_rating_service: RatingService = None
_campaign_service: CampaignService = None


def get_db_service() -> FirestoreService:
    """Get Firestore database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = FirestoreService()
    return _db_service


def get_rating_service() -> RatingService:
    """Get rating service instance."""
    global _rating_service
    if _rating_service is None:
        _rating_service = RatingService()
    return _rating_service


def get_campaign_service() -> CampaignService:
    """Get campaign service instance."""
    global _campaign_service
    if _campaign_service is None:
        _campaign_service = CampaignService(get_db_service())
    return _campaign_service
