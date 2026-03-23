"""
LinkedIn API Client
Integration with LinkedIn API for posting and analytics
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


class LinkedInClient:
    """LinkedIn API client"""
    
    API_BASE_URL = "https://api.linkedin.com/v2"
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 access_token: Optional[str] = None, organization_id: Optional[str] = None):
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.organization_id = organization_id or os.getenv("LINKEDIN_ORGANIZATION_ID")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def test_connection(self) -> Dict:
        """Test API connection"""
        try:
            if requests is None:
                return {"success": False, "connected": False, "error": "requests library not available"}
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/me",
                headers=self.headers
            )
            response.raise_for_status()
            return {
                "success": True,
                "connected": True,
                "data": response.json()
            }
        except Exception as e:
            logger.error(f"LinkedIn connection test failed: {str(e)}")
            return {
                "success": False,
                "connected": False,
                "error": str(e)
            }
    
    def post_content(self, text: str, link: Optional[str] = None, 
                    image_url: Optional[str] = None) -> Dict:
        """Post content to LinkedIn"""
        try:
            # Build post payload
            payload = {
                "author": f"urn:li:organization:{self.organization_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add link if provided
            if link:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "originalUrl": link
                }]
            
            # Add image if provided
            if image_url:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "media": image_url
                }]
            
            response = requests.post(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/ugcPosts",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get("id")
            
            logger.info(f"LinkedIn post published: {post_id}")
            
            return {
                "success": True,
                "platform_post_id": post_id,
                "platform_url": f"https://www.linkedin.com/feed/update/{post_id}",
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LinkedIn post failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a specific post"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/organizationalEntityShareStatistics",
                headers=self.headers,
                params={
                    "q": "organizationalEntity",
                    "organizationalEntity": f"urn:li:organization:{self.organization_id}",
                    "shares": [post_id]
                }
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get("elements", [])
            
            if elements:
                stats = elements[0].get("totalShareStatistics", {})
                return {
                    "success": True,
                    "likes": stats.get("likeCount", 0),
                    "comments": stats.get("commentCount", 0),
                    "shares": stats.get("shareCount", 0),
                    "clicks": stats.get("clickCount", 0),
                    "impressions": stats.get("impressionCount", 0),
                    "engagement": stats.get("engagement", 0)
                }
            
            return {
                "success": True,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "clicks": 0,
                "impressions": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn analytics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_follower_statistics(self) -> Dict:
        """Get follower statistics"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/organizationalEntityFollowerStatistics",
                headers=self.headers,
                params={
                    "q": "organizationalEntity",
                    "organizationalEntity": f"urn:li:organization:{self.organization_id}"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            elements = data.get("elements", [])
            
            if elements:
                stats = elements[0]
                return {
                    "success": True,
                    "followers_count": stats.get("followerCounts", {}).get("organicFollowerCount", 0),
                    "followers_gained": stats.get("followerGains", {}).get("organicFollowerGain", 0)
                }
            
            return {
                "success": True,
                "followers_count": 0,
                "followers_gained": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get follower statistics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
