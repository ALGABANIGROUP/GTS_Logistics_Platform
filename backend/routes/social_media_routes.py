"""
Social Media API Routes
Admin and public endpoints for social media management
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.database.session import get_async_session
from backend.models.social_media import (
    SocialMediaAccount, SocialMediaPost, SocialMediaAnalytics,
    SocialMediaTemplate, SocialMediaSettings, SocialPlatform, PostStatus
)
from backend.models.tenant_social_links import TenantSocialLinks
from backend.security.auth import get_current_user, require_roles
from backend.security.tenant_resolver import get_tenant_id, TenantResolver
from backend.social_media.auto_poster import auto_poster
from backend.social_media.analytics import analytics
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["social-media"])
public_router = APIRouter(tags=["social-media-public"])


# ============================================================================
# Pydantic Models
# ============================================================================

class AccountCreate(BaseModel):
    platform: str
    account_name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None


class PostCreate(BaseModel):
    content: str
    platforms: List[str]
    scheduled_time: Optional[datetime] = None
    link: Optional[str] = None
    hashtags: Optional[List[str]] = None
    image_url: Optional[str] = None


class SettingsUpdate(BaseModel):
    auto_posting_enabled: bool
    auto_post_new_blogs: Optional[bool] = None
    auto_post_new_services: Optional[bool] = None
    default_posting_times: Optional[dict] = None


class SocialLinkItem(BaseModel):
    platform: str  # linkedin, x, facebook, youtube, instagram
    url: str
    enabled: bool = True
    sort_order: int = 0


class SocialLinksUpdate(BaseModel):
    tenant_id: Optional[str] = None  # If not provided, uses current tenant
    links: List[SocialLinkItem]


# ============================================================================
# Admin Routes - Accounts Management
# ============================================================================

@router.get("/accounts")
async def get_connected_accounts(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all connected social media accounts"""
    try:
        result = await db.execute(
            select(SocialMediaAccount).where(SocialMediaAccount.is_active == True)
        )
        accounts = result.scalars().all()
        
        return {
            "success": True,
            "accounts": [
                {
                    "id": account.id,
                    "platform": account.platform,
                    "account_name": account.account_name,
                    "is_connected": account.is_connected,
                    "auto_posting_enabled": account.auto_posting_enabled,
                    "followers_count": account.followers_count,
                    "posts_count": account.posts_count,
                    "last_sync": account.last_sync.isoformat() if account.last_sync is not None else None
                }
                for account in accounts
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect/{platform}")
async def connect_platform(
    platform: str,
    current_user = Depends(get_current_user)
):
    """Initialize platform connection (OAuth flow)"""
    try:
        # This would generate OAuth URL in production
        # For now, return placeholder
        return {
            "success": True,
            "auth_url": f"https://{platform}.com/oauth/authorize?client_id=YOUR_CLIENT_ID",
            "message": "Please authorize the application"
        }
    except Exception as e:
        logger.error(f"Error connecting platform: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect/{platform}")
async def disconnect_platform(
    platform: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Disconnect a platform"""
    try:
        result = await db.execute(
            select(SocialMediaAccount).where(
                and_(
                    SocialMediaAccount.platform == platform,
                    SocialMediaAccount.is_active == True
                )
            )
        )
        account = result.scalar_one_or_none()
            
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
            
        account.is_connected = False  # type: ignore[assignment]
        account.access_token = None  # type: ignore[assignment]
        account.access_token_secret = None  # type: ignore[assignment]
        await db.commit()
            
        return {
            "success": True,
            "message": f"{platform} disconnected successfully"
        }
    except Exception as e:
        logger.error(f"Error disconnecting platform: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/{platform}")
async def sync_platform(
    platform: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Sync data from platform"""
    try:
        result = await db.execute(
            select(SocialMediaAccount).where(
                and_(
                    SocialMediaAccount.platform == platform,
                    SocialMediaAccount.is_connected == True
                )
            )
        )
        account = result.scalar_one_or_none()
            
        if not account:
            raise HTTPException(status_code=404, detail="Account not connected")
            
        # Sync data from platform API
        # This would call the respective client in production
            
        account.last_sync = datetime.utcnow()  # type: ignore[assignment]
        await db.commit()
            
        return {
            "success": True,
            "message": f"{platform} synced successfully"
        }
    except Exception as e:
        logger.error(f"Error syncing platform: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Admin Routes - Posts Management
# ============================================================================

@router.get("/posts")
async def get_posts(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get social media posts"""
    try:
        query = select(SocialMediaPost)
            
        filters = []
        if status:
            filters.append(SocialMediaPost.status == status)
        if platform:
            filters.append(SocialMediaPost.platform == platform)
            
        if filters:
            query = query.where(and_(*filters))
            
        query = query.order_by(SocialMediaPost.created_at.desc()).limit(limit)
            
        result = await db.execute(query)
        posts = result.scalars().all()
            
        return {
            "success": True,
            "posts": [
                {
                    "id": post.id,
                    "content": post.content,
                    "platform": post.platform,
                    "status": post.status,
                    "scheduled_time": post.scheduled_time.isoformat() if post.scheduled_time is not None else None,
                    "published_time": post.published_time.isoformat() if post.published_time is not None else None,
                    "likes_count": post.likes_count,
                    "comments_count": post.comments_count,
                    "shares_count": post.shares_count,
                    "engagement_rate": post.engagement_rate
                }
                for post in posts
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts")
async def create_post(
    post_data: PostCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create and schedule a post"""
    try:
        # Use auto_poster to schedule the post
        content = {
            'text': post_data.content,
            'link': post_data.link,
            'image_url': post_data.image_url,
            'hashtags': post_data.hashtags
        }
        
        result = auto_poster.schedule_post(
            content=content,
            platforms=post_data.platforms,
            schedule_time=post_data.scheduled_time
        )
        
        # Save to database
        for platform in post_data.platforms:
            new_post = SocialMediaPost(
                platform=platform,
                content=post_data.content,
                link_url=post_data.link,
                hashtags=post_data.hashtags,
                scheduled_time=post_data.scheduled_time,
                status=PostStatus.SCHEDULED if post_data.scheduled_time else PostStatus.PUBLISHING,
                created_by=current_user.id
            )
            db.add(new_post)
            
        await db.commit()
        
        return {
            "success": True,
            "message": "Post created successfully",
            "post_id": result.get('id')
        }
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Delete a post"""
    try:
        result = await db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        post = result.scalar_one_or_none()
            
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
            
        post.status = PostStatus.DELETED  # type: ignore[assignment]
        await db.commit()
            
        return {
            "success": True,
            "message": "Post deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Admin Routes - Analytics
# ============================================================================

@router.get("/analytics/summary")
async def get_analytics_summary(
    current_user = Depends(get_current_user)
):
    """Get analytics summary"""
    try:
        platforms = ['linkedin', 'twitter', 'facebook']
        comparison = analytics.compare_platforms(platforms)
        
        return {
            "success": True,
            "totalFollowers": comparison['overall_stats']['total_followers'],
            "engagementRate": comparison['overall_stats']['avg_engagement_rate'],
            "totalReach": comparison['overall_stats']['total_reach'],
            "monthlyPosts": 127,  # This would come from database
            "followerGrowth": 685
        }
    except Exception as e:
        logger.error(f"Error fetching analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{platform}")
async def get_platform_analytics(
    platform: str,
    current_user = Depends(get_current_user)
):
    """Get detailed analytics for a platform"""
    try:
        if platform == 'all':
            platforms = ['linkedin', 'twitter', 'facebook']
            result = analytics.compare_platforms(platforms)
        else:
            result = analytics.collect_platform_metrics(platform)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error fetching platform analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/report/{period}")
async def get_performance_report(
    period: str,
    current_user = Depends(get_current_user)
):
    """Generate performance report"""
    try:
        report = analytics.generate_performance_report(period=period)
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Admin Routes - Settings
# ============================================================================

@router.get("/settings")
async def get_settings(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get social media settings"""
    try:
        result = await db.execute(select(SocialMediaSettings))
        settings = result.scalar_one_or_none()
            
        if not settings:
            settings = SocialMediaSettings()
            db.add(settings)
            await db.commit()
            
        return {
            "success": True,
            "settings": {
                "auto_posting_enabled": settings.auto_posting_enabled,
                "auto_post_new_blogs": settings.auto_post_new_blogs,
                "auto_post_new_services": settings.auto_post_new_services,
                "optimal_posting_enabled": settings.optimal_posting_enabled,
                "max_posts_per_day": settings.max_posts_per_day
            }
        }
    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_settings(
    settings_data: SettingsUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update social media settings"""
    try:
        result = await db.execute(select(SocialMediaSettings))
        settings = result.scalar_one_or_none()
            
        if not settings:
            settings = SocialMediaSettings()
            db.add(settings)
            
        settings.auto_posting_enabled = settings_data.auto_posting_enabled  # type: ignore[assignment]
        if settings_data.auto_post_new_blogs is not None:
            settings.auto_post_new_blogs = settings_data.auto_post_new_blogs  # type: ignore[assignment]
        if settings_data.auto_post_new_services is not None:
            settings.auto_post_new_services = settings_data.auto_post_new_services  # type: ignore[assignment]
            
        settings.updated_by = current_user.id
        await db.commit()
            
        return {
            "success": True,
            "message": "Settings updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Public Routes - For Frontend Display
# ============================================================================

@public_router.get("/settings/social-links-legacy")
async def get_social_links():
    """Get public social media links"""
    try:
        # This would come from database in production
        links = [
            {
                "platform": "linkedin",
                "url": "https://linkedin.com/company/gabanilogistics",
                "icon": "💼",
                "displayName": "LinkedIn",
                "description": "Professional networking and career opportunities"
            },
            {
                "platform": "twitter",
                "url": "https://twitter.com/gabanilogistics",
                "icon": "🐦",
                "displayName": "Twitter",
                "description": "Quick updates and industry news"
            },
            {
                "platform": "facebook",
                "url": "https://facebook.com/gabanilogistics",
                "icon": "📘",
                "displayName": "Facebook",
                "description": "Community content and events"
            },
            {
                "platform": "youtube",
                "url": "https://youtube.com/@gabanilogistics",
                "icon": "🎬",
                "displayName": "YouTube",
                "description": "Educational videos and tutorials"
            }
        ]
        
        return {
            "success": True,
            "links": links
        }
    except Exception as e:
        logger.error(f"Error fetching social links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@public_router.get("/recent-posts/{platform}")
async def get_recent_public_posts(
    platform: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_async_session)
):
    """Get recent public posts for a platform"""
    try:
        result = await db.execute(
            select(SocialMediaPost)
            .where(
                and_(
                    SocialMediaPost.platform == platform,
                    SocialMediaPost.status == PostStatus.PUBLISHED
                )
            )
            .order_by(SocialMediaPost.published_time.desc())
            .limit(limit)
        )
        posts = result.scalars().all()
            
        return {
            "success": True,
            "posts": [
                {
                    "id": post.id,
                    "content": post.content[:200],  # Truncate for preview
                    "published_at": post.published_time.isoformat() if post.published_time is not None else None,
                    "likes_count": post.likes_count,
                    "comments_count": post.comments_count
                }
                for post in posts
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching recent posts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Social Links Settings (Tenant-specific branding)
# ============================================================================

@router.get("/settings/social-links")
async def get_social_links(
    request: Request,
    tenant_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get social media links for a tenant (branding/footer)"""
    try:
        # Resolve tenant - get tenant_id from JWT or headers
        resolved_tenant_id = current_user.get("tenant_id")
        if not resolved_tenant_id:
            resolved_tenant = await TenantResolver.resolve_tenant(request, db)
            resolved_tenant_id = resolved_tenant.id if resolved_tenant else "gts"  # Default to "gts"

        # Use provided tenant_id or resolved tenant
        target_tenant_id = tenant_id or resolved_tenant_id

        # Check permissions: Super admin can see all, others only their own
        user_role = current_user.get("role_key") or current_user.get("role")
        if user_role not in ["super_admin", "owner"] and tenant_id and target_tenant_id != resolved_tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        result = await db.execute(
            select(TenantSocialLinks)
            .where(TenantSocialLinks.tenant_id == target_tenant_id)
            .order_by(TenantSocialLinks.sort_order, TenantSocialLinks.platform)
        )
        links = result.scalars().all()

        return {
            "success": True,
            "tenant_id": target_tenant_id,
            "links": [
                {
                    "platform": link.platform,
                    "url": link.url,
                    "enabled": link.enabled,
                    "sort_order": link.sort_order
                }
                for link in links
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching social links: {str(e)}")
        # Return empty list on error (graceful degradation)
        return {
            "success": True,
            "tenant_id": tenant_id,
            "links": []
        }


@router.put("/settings/social-links")
async def update_social_links(
    update_data: SocialLinksUpdate,
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Update social media links for a tenant (Admin and Super Admin)"""
    try:
        # Admin, owner, and super admin can update social links
        user_role = current_user.get("role_key") or current_user.get("role")
        if user_role not in ["admin", "owner", "super_admin"]:
            raise HTTPException(status_code=403, detail="Only admin and super admin can update social links")

        # Resolve tenant - get tenant_id from JWT or headers
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            resolved_tenant = await TenantResolver.resolve_tenant(request, db)
            tenant_id = resolved_tenant.id if resolved_tenant else "gts"  # Default to "gts"

        # Use provided tenant_id or resolved tenant
        target_tenant_id = update_data.tenant_id or tenant_id

        # Delete existing links for this tenant
        await db.execute(
            TenantSocialLinks.__table__.delete().where(
                TenantSocialLinks.tenant_id == target_tenant_id
            )
        )

        # Insert new links
        for link_data in update_data.links:
            link = TenantSocialLinks(
                tenant_id=target_tenant_id,
                platform=link_data.platform,
                url=link_data.url,
                enabled=link_data.enabled,
                sort_order=link_data.sort_order,
                updated_by=str(current_user.get("id"))  # Convert to string
            )
            db.add(link)

        await db.commit()

        return {
            "success": True,
            "message": f"Updated {len(update_data.links)} social links for tenant {target_tenant_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating social links: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Public Routes (Footer consumption)
# ============================================================================

@public_router.get("/links")
async def get_social_media_links(
    request: Request,
    tenant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """Public endpoint to get social links for footer (no auth required)."""
    try:
        target_tenant_id = tenant_id

        if not target_tenant_id:
            try:
                tenant = await TenantResolver.resolve_tenant(request, db)
                target_tenant_id = getattr(tenant, "id", None) if tenant else None
            except Exception:
                target_tenant_id = None

        if not target_tenant_id:
            return {"links": []}

        result = await db.execute(
            select(TenantSocialLinks)
            .where(
                and_(
                    TenantSocialLinks.tenant_id == target_tenant_id,
                    TenantSocialLinks.enabled == True,
                )
            )
            .order_by(TenantSocialLinks.sort_order, TenantSocialLinks.platform)
        )
        links = result.scalars().all()

        return {
            "links": [
                {
                    "platform": link.platform,
                    "url": link.url,
                    "enabled": link.enabled,
                    "sort_order": link.sort_order,
                }
                for link in links
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching public social links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Admin Routes - Social Media Links Management
# ============================================================================

@router.get("/links")
async def get_admin_social_links(
    tenant_id: Optional[str] = None,
    current_user = Depends(require_roles(["admin", "super_admin"])),
    db: AsyncSession = Depends(get_async_session)
):
    """Admin endpoint to get all social links for a tenant"""
    try:
        target_tenant_id = tenant_id or get_tenant_id(current_user)

        result = await db.execute(
            select(TenantSocialLinks)
            .where(TenantSocialLinks.tenant_id == target_tenant_id)
            .order_by(TenantSocialLinks.sort_order, TenantSocialLinks.platform)
        )
        links = result.scalars().all()

        return {
            "links": [
                {
                    "platform": link.platform,
                    "url": link.url,
                    "enabled": link.enabled,
                    "sort_order": link.sort_order
                }
                for link in links
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching admin social links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/links")
async def update_social_links(
    links_data: SocialLinksUpdate,
    current_user = Depends(require_roles(["admin", "super_admin"])),
    db: AsyncSession = Depends(get_async_session)
):
    """Admin endpoint to update social links for a tenant"""
    try:
        target_tenant_id = links_data.tenant_id or get_tenant_id(current_user)

        # Verify permissions for cross-tenant access
        if links_data.tenant_id and links_data.tenant_id != get_tenant_id(current_user):
            if not current_user.get("role") == "super_admin":
                raise HTTPException(status_code=403, detail="Super admin access required for cross-tenant operations")

        # Delete existing links for this tenant
        await db.execute(
            select(TenantSocialLinks).where(TenantSocialLinks.tenant_id == target_tenant_id).delete()
        )

        # Insert new links
        for link_data in links_data.links:
            new_link = TenantSocialLinks(
                tenant_id=target_tenant_id,
                platform=link_data.platform,
                url=link_data.url,
                enabled=link_data.enabled,
                sort_order=link_data.sort_order
            )
            db.add(new_link)

        await db.commit()

        return {
            "success": True,
            "message": "Social media links updated successfully",
            "links": links_data.links
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating social links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Platform Social Links (Footer)
# ============================================================================

@public_router.get("/settings/social-links")
async def get_platform_social_links(db: AsyncSession = Depends(get_async_session)):
    """Public endpoint to get platform social media links for footer"""
    try:
        from backend.services.platform_settings_store import get_platform_settings
        settings = await get_platform_settings(db)
        social_links = settings.get("social_links", {})
        return social_links
    except Exception as e:
        logger.error(f"Error fetching platform social links: {str(e)}")
        # Return empty links on error for resilience
        return {
            "linkedin": "",
            "x": "",
            "facebook": "",
            "youtube": "",
            "instagram": "",
        }


@router.get("/settings/platform-social-links")
async def get_admin_platform_social_links(
    current_user = Depends(require_roles(["admin", "super_admin"])),
    db: AsyncSession = Depends(get_async_session)
):
    """Admin endpoint to get platform social media links"""
    return await get_platform_social_links(db)


@router.put("/settings/platform-social-links")
async def update_platform_social_links(
    links: dict,
    current_user = Depends(require_roles(["admin", "super_admin"])),
    db: AsyncSession = Depends(get_async_session)
):
    """Admin endpoint to update platform social media links"""
    try:
        from backend.services.platform_settings_store import update_platform_settings
        # Validate links structure
        expected_keys = {"linkedin", "x", "facebook", "youtube", "instagram"}
        if not isinstance(links, dict):
            raise HTTPException(status_code=400, detail="Links must be a dictionary")
        for key in links:
            if key not in expected_keys:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {key}")
            if not isinstance(links[key], str):
                raise HTTPException(status_code=400, detail=f"Link for {key} must be a string")

        # Update settings
        updated = await update_platform_settings(db, {"social_links": links}, updated_by=current_user.get("email", "admin"))
        return {"success": True, "links": updated.get("social_links", {})}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating platform social links: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

