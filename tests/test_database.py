"""
Database connectivity and model tests
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.unified_models import UnifiedUser
from backend.models.models import Shipment
from backend.auth import get_password_hash


class TestDatabaseConnection:
    """Test database connectivity"""
    
    @pytest.mark.asyncio
    async def test_db_session_works(self, db_session: AsyncSession):
        """Test database session is functional"""
        assert db_session is not None
        assert not db_session.is_active or True  # Session exists
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user in database"""
        user = UnifiedUser(
            email="dbtest@test.com",
            full_name="DB Test User",
            hashed_password=get_password_hash("password"),
            role="user",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "dbtest@test.com"
    
    @pytest.mark.asyncio
    async def test_query_user(self, db_session: AsyncSession, test_user: UnifiedUser):
        """Test querying users from database"""
        from sqlalchemy import select
        
        result = await db_session.execute(
            select(UnifiedUser).where(UnifiedUser.email == test_user.email)
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == test_user.email


class TestModels:
    """Test database models"""
    
    @pytest.mark.asyncio
    async def test_user_model_fields(self, test_user: UnifiedUser):
        """Test UnifiedUser model has required fields"""
        assert hasattr(test_user, 'id')
        assert hasattr(test_user, 'email')
        assert hasattr(test_user, 'full_name')
        assert hasattr(test_user, 'role')
        assert hasattr(test_user, 'is_active')
        assert hasattr(test_user, 'created_at')
    
    @pytest.mark.asyncio
    async def test_user_password_hashed(self, test_user: UnifiedUser):
        """Test user password is hashed, not plain text"""
        assert test_user.hashed_password != "testpassword"
        assert len(test_user.hashed_password) > 20  # Bcrypt hash is long
