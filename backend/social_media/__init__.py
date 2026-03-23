"""
Social Media Integration Module
Centralized social media management for GTS Logistics
"""

from backend.social_media.linkedin_client import LinkedInClient
from backend.social_media.twitter_client import TwitterClient
from backend.social_media.facebook_client import FacebookClient
from backend.social_media.auto_poster import AutoPoster, auto_poster
from backend.social_media.analytics import SocialAnalytics, analytics

__all__ = [
    'LinkedInClient',
    'TwitterClient',
    'FacebookClient',
    'AutoPoster',
    'auto_poster',
    'SocialAnalytics',
    'analytics'
]

__version__ = '1.0.0'
__author__ = 'GTS Logistics Team'
