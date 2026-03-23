"""
Twitter API Client
Integration with Twitter API v2 for posting and analytics
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


class TwitterClient:
    """Twitter API v2 client"""
    
    API_BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 access_token: Optional[str] = None, access_secret: Optional[str] = None,
                 bearer_token: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self.access_token = access_token or os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = access_secret or os.getenv("TWITTER_ACCESS_SECRET")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict:
        """Test API connection"""
        try:
            if requests is None:
                return {"success": False, "connected": False, "error": "requests library not available"}
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/users/me",
                headers=self.headers
            )
            response.raise_for_status()
            return {
                "success": True,
                "connected": True,
                "data": response.json()
            }
        except Exception as e:
            logger.error(f"Twitter connection test failed: {str(e)}")
            return {
                "success": False,
                "connected": False,
                "error": str(e)
            }
    
    def tweet(self, text: str, image_path: Optional[str] = None, 
             reply_to: Optional[str] = None) -> Dict:
        """Post a tweet"""
        try:
            payload = {"text": text}
            
            # Add reply settings if replying to another tweet
            if reply_to:
                payload["reply"] = {  # type: ignore[assignment]
                    "in_reply_to_tweet_id": reply_to
                }
            
            # Upload media if image provided
            if image_path:
                media_id = self._upload_media(image_path)
                if media_id:
                    payload["media"] = {  # type: ignore[assignment]
                        "media_ids": [media_id]
                    }
            
            response = requests.post(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/tweets",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            tweet_data = result.get("data", {})
            tweet_id = tweet_data.get("id")
            
            logger.info(f"Tweet published: {tweet_id}")
            
            return {
                "success": True,
                "platform_post_id": tweet_id,
                "platform_url": f"https://twitter.com/i/web/status/{tweet_id}",
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tweet failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_media(self, image_path: str) -> Optional[str]:
        """Upload media to Twitter"""
        try:
            # Use Twitter upload API v1.1 for media
            upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            
            with open(image_path, 'rb') as image_file:
                files = {'media': image_file}
                
                # OAuth1 authentication required for upload
                # Simplified version - in production use proper OAuth1
                response = requests.post(upload_url, files=files)  # type: ignore[union-attr]
                response.raise_for_status()
                
                result = response.json()
                return result.get("media_id_string")
                
        except Exception as e:
            logger.error(f"Media upload failed: {str(e)}")
            return None
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get metrics for a specific tweet"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/tweets/{tweet_id}",
                headers=self.headers,
                params={
                    "tweet.fields": "public_metrics,non_public_metrics,organic_metrics"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            tweet_data = data.get("data", {})
            
            public_metrics = tweet_data.get("public_metrics", {})
            organic_metrics = tweet_data.get("organic_metrics", {})
            
            return {
                "success": True,
                "likes": public_metrics.get("like_count", 0),
                "retweets": public_metrics.get("retweet_count", 0),
                "replies": public_metrics.get("reply_count", 0),
                "quotes": public_metrics.get("quote_count", 0),
                "impressions": organic_metrics.get("impression_count", 0),
                "url_clicks": organic_metrics.get("url_link_clicks", 0),
                "engagement": (
                    public_metrics.get("like_count", 0) +
                    public_metrics.get("retweet_count", 0) +
                    public_metrics.get("reply_count", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get tweet metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_metrics(self) -> Dict:
        """Get user account metrics"""
        try:
            response = requests.get(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/users/me",
                headers=self.headers,
                params={
                    "user.fields": "public_metrics"
                }
            )
            response.raise_for_status()
            
            data = response.json()
            user_data = data.get("data", {})
            metrics = user_data.get("public_metrics", {})
            
            return {
                "success": True,
                "followers_count": metrics.get("followers_count", 0),
                "following_count": metrics.get("following_count", 0),
                "tweet_count": metrics.get("tweet_count", 0),
                "listed_count": metrics.get("listed_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_tweet(self, tweet_id: str) -> Dict:
        """Delete a tweet"""
        try:
            response = requests.delete(  # type: ignore[union-attr]
                f"{self.API_BASE_URL}/tweets/{tweet_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "deleted": True
            }
            
        except Exception as e:
            logger.error(f"Failed to delete tweet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
