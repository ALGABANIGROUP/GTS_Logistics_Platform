"""
Auto-Posting System
Automated social media content posting with scheduling
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

try:
    import schedule  # type: ignore
except ImportError:  # pragma: no cover
    schedule = None  # type: ignore

from backend.social_media.linkedin_client import LinkedInClient
from backend.social_media.twitter_client import TwitterClient
from backend.social_media.facebook_client import FacebookClient

logger = logging.getLogger(__name__)


class SocialPlatform(str, Enum):
    """Social media platforms"""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class ContentType(str, Enum):
    """Content types"""
    BLOG_POST = "blog_post"
    SERVICE_LAUNCH = "service_launch"
    INDUSTRY_NEWS = "industry_news"
    COMPANY_UPDATE = "company_update"
    PROMOTION = "promotion"
    GENERAL = "general"


class AutoPoster:
    """Automated social media posting system"""
    
    def __init__(self):
        self.connected_platforms: Dict[SocialPlatform, bool] = {}
        self.posting_schedule: Dict[str, str] = {}
        self.content_queue: List[Dict] = []
        self.clients = {}
        
        # Performance thresholds
        self.max_posts_per_day = 10
        self.min_post_interval_minutes = 60
        self.last_post_times = {}
        
        logger.info("AutoPoster initialized")
    
    def initialize_platforms(self, api_keys: Dict):
        """Initialize platform connections"""
        for platform_name, keys in api_keys.items():
            try:
                platform = SocialPlatform(platform_name)
                
                if self._validate_api_keys(platform, keys):
                    self._connect_platform(platform, keys)
                    logger.info(f"Connected to {platform.value}")
                else:
                    logger.warning(f"Invalid API keys for {platform.value}")
                    
            except Exception as e:
                logger.error(f"Error connecting to {platform_name}: {str(e)}")
    
    def _validate_api_keys(self, platform: SocialPlatform, keys: Dict) -> bool:
        """Validate API keys for a platform"""
        required_keys = {
            SocialPlatform.LINKEDIN: ["client_id", "client_secret", "access_token"],
            SocialPlatform.TWITTER: ["api_key", "api_secret", "access_token", "access_secret"],
            SocialPlatform.FACEBOOK: ["app_id", "app_secret", "page_access_token"]
        }
        
        platform_keys = required_keys.get(platform, [])
        return all(key in keys and keys[key] for key in platform_keys)
    
    def _connect_platform(self, platform: SocialPlatform, api_keys: Dict):
        """Connect to a platform"""
        try:
            if platform == SocialPlatform.LINKEDIN:
                self.clients[platform] = LinkedInClient(**api_keys)
                
            elif platform == SocialPlatform.TWITTER:
                self.clients[platform] = TwitterClient(**api_keys)
                
            elif platform == SocialPlatform.FACEBOOK:
                self.clients[platform] = FacebookClient(**api_keys)
            
            # Test connection
            test_result = self.clients[platform].test_connection()
            self.connected_platforms[platform] = test_result.get("connected", False)
            
        except Exception as e:
            logger.error(f"Failed to connect to {platform.value}: {str(e)}")
            self.connected_platforms[platform] = False
    
    def schedule_post(self, content: Dict, platforms: List[str], 
                     schedule_time: Optional[datetime] = None) -> Dict:
        """Schedule a post for publishing"""
        post_data = {
            'id': f"post_{int(datetime.now().timestamp())}",
            'content': content,
            'platforms': platforms,
            'scheduled_time': schedule_time or datetime.now(),
            'status': 'scheduled',
            'created_at': datetime.now()
        }
        
        self.content_queue.append(post_data)
        
        # Schedule the post
        if schedule_time:
            delay_seconds = (schedule_time - datetime.now()).total_seconds()
            if delay_seconds > 0:
                timer = threading.Timer(delay_seconds, self._publish_post, [post_data])
                timer.start()
        else:
            # Publish immediately
            self._publish_post(post_data)
        
        logger.info(f"Scheduled post {post_data['id']} for {schedule_time}")
        return post_data
    
    def _publish_post(self, post_data: Dict):
        """Publish a post to specified platforms"""
        try:
            content = post_data['content']
            platforms = post_data['platforms']
            
            results = {}
            
            for platform_name in platforms:
                platform = SocialPlatform(platform_name)
                
                if not self.connected_platforms.get(platform, False):
                    results[platform_name] = {
                        'success': False, 
                        'error': 'Platform not connected'
                    }
                    continue
                
                # Check rate limiting
                if not self._can_post_to_platform(platform):
                    results[platform_name] = {
                        'success': False,
                        'error': 'Rate limit exceeded'
                    }
                    continue
                
                try:
                    client = self.clients[platform]
                    
                    if platform == SocialPlatform.LINKEDIN:
                        result = client.post_content(
                            text=content.get('text', ''),
                            link=content.get('link'),
                            image_url=content.get('image_url')
                        )
                        
                    elif platform == SocialPlatform.TWITTER:
                        result = client.tweet(
                            text=content.get('text', ''),
                            image_path=content.get('image_path')
                        )
                        
                    elif platform == SocialPlatform.FACEBOOK:
                        result = client.create_post(
                            message=content.get('text', ''),
                            link=content.get('link'),
                            image_url=content.get('image_url')
                        )
                    
                    results[platform_name] = result
                    
                    if result.get('success'):
                        self._update_last_post_time(platform)
                        logger.info(f"Published to {platform_name}")
                    
                except Exception as e:
                    results[platform_name] = {'success': False, 'error': str(e)}
                    logger.error(f"Error publishing to {platform_name}: {str(e)}")
            
            # Update post status
            post_data['status'] = 'published'
            post_data['published_at'] = datetime.now()
            post_data['results'] = results
            
            return results
            
        except Exception as e:
            logger.error(f"Error in _publish_post: {str(e)}")
            return {'error': str(e)}
    
    def _can_post_to_platform(self, platform: SocialPlatform) -> bool:
        """Check if we can post to a platform (rate limiting)"""
        last_post = self.last_post_times.get(platform)
        
        if not last_post:
            return True
        
        time_since_last_post = (datetime.now() - last_post).total_seconds() / 60
        return time_since_last_post >= self.min_post_interval_minutes
    
    def _update_last_post_time(self, platform: SocialPlatform):
        """Update last post time for a platform"""
        self.last_post_times[platform] = datetime.now()
    
    def auto_post_new_content(self, content_type: str, content_data: Dict):
        """Automatically post new content"""
        # Determine platforms for content type
        platforms = self._determine_platforms_for_content(content_type)
        
        # Generate post text
        post_text = self._generate_post_text(content_type, content_data)
        
        # Create post content
        post_content = {
            'text': post_text,
            'link': content_data.get('url'),
            'image_url': content_data.get('image_url')
        }
        
        # Get optimal posting time
        scheduled_time = self._get_optimal_posting_time()
        
        return self.schedule_post(
            content=post_content,
            platforms=platforms,
            schedule_time=scheduled_time
        )
    
    def _determine_platforms_for_content(self, content_type: str) -> List[str]:
        """Determine appropriate platforms for content type"""
        platform_mapping = {
            'blog_post': ['linkedin', 'twitter', 'facebook'],
            'service_launch': ['linkedin', 'facebook'],
            'industry_news': ['twitter', 'linkedin'],
            'company_update': ['linkedin', 'facebook'],
            'promotion': ['twitter', 'facebook', 'instagram']
        }
        
        return platform_mapping.get(content_type, ['linkedin', 'twitter'])
    
    def _generate_post_text(self, content_type: str, data: Dict) -> str:
        """Generate post text from template"""
        templates = {
            'blog_post': (
                f"📚 New Article: {data.get('title', '')}\n\n"
                f"{data.get('excerpt', '')}\n\n"
                f"🔗 Read more: {data.get('url', '')}\n\n"
                f"#{data.get('hashtags', 'logistics #freightmanagement')}"
            ),
            'service_launch': (
                f"🎉 Announcing a New Service!\n\n"
                f"{data.get('service_name', '')}: {data.get('description', '')}\n\n"
                f"Learn more: {data.get('url', '')}\n\n"
                f"#NewServices #FreightLogistics"
            ),
            'industry_news': (
                f"📰 Breaking News: {data.get('title', '')}\n\n"
                f"{data.get('summary', '')}\n\n"
                f"#{data.get('hashtags', 'logistics #industry')}"
            ),
            'company_update': (
                f"🏢 Update: {data.get('update', '')}\n\n"
                f"{data.get('details', '')}\n\n"
                f"#CompanyNews #Growth"
            ),
            'promotion': (
                f"🔥 Special Offer!\n\n"
                f"{data.get('offer', '')}\n\n"
                f"Don't miss out: {data.get('url', '')}\n\n"
                f"#{data.get('hashtags', 'promotion #logistics')}"
            )
        }
        
        return templates.get(content_type, data.get('text', '') or '')
    
    def _get_optimal_posting_time(self) -> datetime:
        """Get optimal posting time"""
        now = datetime.now()
        
        # Optimal posting times
        optimal_times = [
            now.replace(hour=9, minute=0, second=0, microsecond=0),   # 9 AM
            now.replace(hour=13, minute=0, second=0, microsecond=0),  # 1 PM
            now.replace(hour=19, minute=0, second=0, microsecond=0),  # 7 PM
        ]
        
        # Find next available time
        future_times = [t for t in optimal_times if t > now]
        
        if future_times:
            return future_times[0]
        else:
            # Next day at 9 AM
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    def start_scheduler(self):
        """Start the posting scheduler"""
        if schedule is None:
            logger.error("schedule library not available; scheduler not started")
            return

        # Daily content check
        schedule.every().day.at("08:00").do(self._daily_content_check)
        
        # Analytics report
        schedule.every().day.at("17:00").do(self._generate_daily_report)
        
        # Cleanup old posts
        schedule.every().day.at("00:00").do(self._cleanup_old_posts)
        
        logger.info("Social media scheduler started")
        
        # Run scheduler in background
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def _daily_content_check(self):
        """Check for new content to post"""
        try:
            logger.info("Running daily content check")
            # This would fetch new content from database
            # and auto-post based on settings
            
        except Exception as e:
            logger.error(f"Error in daily content check: {str(e)}")
    
    def _generate_daily_report(self):
        """Generate daily analytics report"""
        try:
            logger.info("Generating daily analytics report")
            # This would generate and send analytics report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
    
    def _cleanup_old_posts(self):
        """Clean up old posts from queue"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            self.content_queue = [
                post for post in self.content_queue 
                if post['created_at'] > cutoff_date
            ]
            logger.info("Cleaned up old posts")
            
        except Exception as e:
            logger.error(f"Error cleaning up posts: {str(e)}")


# Global auto poster instance
auto_poster = AutoPoster()


def start_auto_poster_thread():
    """Start auto poster in background thread"""
    scheduler_thread = threading.Thread(target=auto_poster.start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("Auto poster thread started")
