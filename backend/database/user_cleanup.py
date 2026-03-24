"""
User Cleanup Service - Manage inactive users and accounts
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserCleanupService:
    """
    Service for managing inactive users and account cleanup
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.inactive_days = 90  # Days after which user is considered inactive
        self.soft_delete_days = 180  # Days after which user is soft-deleted
        self.hard_delete_days = 365  # Days after which user is hard-deleted

    async def find_inactive_users(self, days: int = None) -> List[Dict[str, Any]]:
        """Find users inactive for specified days"""
        days = days or self.inactive_days
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            from backend.models.user import User
            
            query = select(User).where(
                User.last_login < cutoff,
                User.is_active == True,
                User.deleted_at.is_(None)
            )
            result = await self.session.execute(query)
            users = result.scalars().all()
            
            return [
                {
                    "id": u.id,
                    "email": u.email,
                    "last_login": u.last_login.isoformat() if u.last_login else None,
                    "inactive_days": days
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"Failed to find inactive users: {e}")
            return []

    async def mark_inactive(self, user_ids: List[int]) -> int:
        """Mark users as inactive"""
        try:
            from backend.models.user import User
            
            query = update(User).where(
                User.id.in_(user_ids),
                User.is_active == True
            ).values(
                is_active=False,
                updated_at=datetime.now()
            )
            result = await self.session.execute(query)
            await self.session.commit()
            
            logger.info(f"Marked {result.rowcount} users as inactive")
            return result.rowcount
        except Exception as e:
            logger.error(f"Failed to mark users inactive: {e}")
            await self.session.rollback()
            return 0

    async def soft_delete_users(self, user_ids: List[int]) -> int:
        """Soft delete users (mark as deleted)"""
        try:
            from backend.models.user import User
            
            query = update(User).where(
                User.id.in_(user_ids),
                User.deleted_at.is_(None)
            ).values(
                deleted_at=datetime.now(),
                is_active=False,
                updated_at=datetime.now()
            )
            result = await self.session.execute(query)
            await self.session.commit()
            
            logger.info(f"Soft deleted {result.rowcount} users")
            return result.rowcount
        except Exception as e:
            logger.error(f"Failed to soft delete users: {e}")
            await self.session.rollback()
            return 0

    async def hard_delete_users(self, user_ids: List[int]) -> int:
        """Permanently delete users and their data"""
        try:
            from backend.models.user import User
            
            # Delete related data first
            # This would need to handle cascades based on your schema
            
            # Then delete users
            query = delete(User).where(User.id.in_(user_ids))
            result = await self.session.execute(query)
            await self.session.commit()
            
            logger.info(f"Hard deleted {result.rowcount} users")
            return result.rowcount
        except Exception as e:
            logger.error(f"Failed to hard delete users: {e}")
            await self.session.rollback()
            return 0

    async def cleanup_orphaned_sessions(self) -> int:
        """Clean up orphaned user sessions"""
        try:
            from backend.models.session import UserSession
            
            cutoff = datetime.now() - timedelta(days=30)
            query = delete(UserSession).where(UserSession.last_activity < cutoff)
            result = await self.session.execute(query)
            await self.session.commit()
            
            logger.info(f"Cleaned up {result.rowcount} orphaned sessions")
            return result.rowcount
        except Exception as e:
            logger.error(f"Failed to clean up sessions: {e}")
            await self.session.rollback()
            return 0

    async def run_full_cleanup(self) -> Dict[str, int]:
        """Run complete user cleanup process"""
        results = {}
        
        # Find inactive users
        inactive = await self.find_inactive_users()
        if inactive:
            inactive_ids = [u["id"] for u in inactive]
            results["inactive_marked"] = await self.mark_inactive(inactive_ids)
        
        # Find users for soft delete
        soft_cutoff = datetime.now() - timedelta(days=self.soft_delete_days)
        try:
            from backend.models.user import User
            query = select(User).where(
                User.last_login < soft_cutoff,
                User.is_active == False,
                User.deleted_at.is_(None)
            )
            result = await self.session.execute(query)
            soft_users = result.scalars().all()
            if soft_users:
                soft_ids = [u.id for u in soft_users]
                results["soft_deleted"] = await self.soft_delete_users(soft_ids)
        except Exception as e:
            logger.error(f"Failed to find users for soft delete: {e}")
        
        # Find users for hard delete
        hard_cutoff = datetime.now() - timedelta(days=self.hard_delete_days)
        try:
            from backend.models.user import User
            query = select(User).where(
                User.deleted_at < hard_cutoff
            )
            result = await self.session.execute(query)
            hard_users = result.scalars().all()
            if hard_users:
                hard_ids = [u.id for u in hard_users]
                results["hard_deleted"] = await self.hard_delete_users(hard_ids)
        except Exception as e:
            logger.error(f"Failed to find users for hard delete: {e}")
        
        # Clean up sessions
        results["sessions_cleaned"] = await self.cleanup_orphaned_sessions()
        
        return results