"""
Facebook API Client
Integration with Facebook Graph API for posting and analytics
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger(__name__)


class FacebookClient:
    """Facebook Graph API client"""
    
    API_BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None,
                 page_access_token: Optional[str] = None, page_id: Optional[str] = None):
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.page_access_token = page_access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID")
    
    def test_connection(self) -> Dict:
        """Test API connection"""
        try:
            if requests is None:
                return {"success": False, "connected": False, "error": "requests library not available"}
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/me",
                params={
                    "access_token": self.page_access_token,
                    "fields": "id,name"
                }
            )
            response.raise_for_status()
            return {
                "success": True,
                "connected": True,
                "data": response.json()
            }
        except Exception as e:
            logger.error(f"Facebook connection test failed: {str(e)}")
            return {
                "success": False,
                "connected": False,
                "error": str(e)
            }
    
    def create_post(self, message: str, link: Optional[str] = None, 
                   image_url: Optional[str] = None, video_url: Optional[str] = None) -> Dict:
        """Create a post on Facebook page"""
        try:
            endpoint = f"{self.API_BASE_URL}/{self.page_id}/feed"
            
            params = {
                "access_token": self.page_access_token,
                "message": message
            }
            
            # Add link if provided
            if link:
                params["link"] = link
            
            # Add photo if provided
            if image_url:
                endpoint = f"{self.API_BASE_URL}/{self.page_id}/photos"
                params["url"] = image_url
                params["caption"] = message
                del params["message"]
            
            # Add video if provided
            if video_url:
                endpoint = f"{self.API_BASE_URL}/{self.page_id}/videos"
                params["file_url"] = video_url
                params["description"] = message
                del params["message"]
            
            response = requests.post(endpoint, params=params)  # type: ignore[union-attr]
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get("id")
            
            logger.info(f"Facebook post published: {post_id}")
            
            return {
                "success": True,
                "platform_post_id": post_id,
                "platform_url": f"https://www.facebook.com/{post_id}",
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Facebook post failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_post_insights(self, post_id: str) -> Dict:
        """Get insights for a specific post"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/{post_id}/insights",
                params={
                    "access_token": self.page_access_token,
                    "metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            insights = data.get("data", [])
            
            metrics = {}
            for insight in insights:
                name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    metrics[name] = values[0].get("value", 0)
            
            return {
                "success": True,
                "impressions": metrics.get("post_impressions", 0),
                "engaged_users": metrics.get("post_engaged_users", 0),
                "clicks": metrics.get("post_clicks", 0),
                "reactions": metrics.get("post_reactions_by_type_total", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get Facebook insights: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_post_engagement(self, post_id: str) -> Dict:
        """Get engagement metrics for a post"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/{post_id}",
                params={
                    "access_token": self.page_access_token,
                    "fields": "likes.summary(true),comments.summary(true),shares"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            likes = data.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = data.get("shares", {}).get("count", 0)
            
            return {
                "success": True,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "engagement": likes + comments + shares
            }
            
        except Exception as e:
            logger.error(f"Failed to get post engagement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_page_insights(self, period: str = "day") -> Dict:
        """Get page insights"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/{self.page_id}/insights",
                params={
                    "access_token": self.page_access_token,
                    "metric": "page_fans,page_impressions,page_engaged_users,page_post_engagements",
                    "period": period
                }
            )
            response.raise_for_status()
            
            data = response.json()
            insights = data.get("data", [])
            
            metrics = {}
            for insight in insights:
                name = insight.get("name")
                values = insight.get("values", [])
                if values:
                    metrics[name] = values[0].get("value", 0)
            
            return {
                "success": True,
                "fans": metrics.get("page_fans", 0),
                "impressions": metrics.get("page_impressions", 0),
                "engaged_users": metrics.get("page_engaged_users", 0),
                "post_engagements": metrics.get("page_post_engagements", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get page insights: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete a post"""
        try:
            response = requests.delete(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/{post_id}",
                params={
                    "access_token": self.page_access_token
                }
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "deleted": True
            }
            
        except Exception as e:
            logger.error(f"Failed to delete post: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
