"""
Services package initialization.
"""

from src.services.firestore_service import FirestoreService
from src.services.rating_service import RatingService
from src.services.campaign_service import CampaignService

# Alias for backward compatibility and clearer intent
DatabaseService = FirestoreService

__all__ = ["FirestoreService", "DatabaseService", "RatingService", "CampaignService"]
