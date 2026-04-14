"""Database and model smoke checks without live DDL."""

import pytest

from backend.auth import get_password_hash
from backend.database.base import Base
from backend.models.models import Shipment
from backend.models.unified_models import UnifiedUser


class TestDatabaseConnection:
    @pytest.mark.asyncio
    async def test_metadata_is_loaded(self):
        assert Base.metadata is not None
        assert len(Base.metadata.tables) > 0

    @pytest.mark.asyncio
    async def test_password_hash_helper(self):
        hashed = get_password_hash("password")
        assert hashed != "password"
        assert len(hashed) > 20


class TestModels:
    @pytest.mark.asyncio
    async def test_unified_user_model_fields(self):
        columns = set(UnifiedUser.__table__.columns.keys())
        assert {"id", "email", "full_name", "password_hash", "is_active"}.issubset(columns)

    @pytest.mark.asyncio
    async def test_shipment_model_exists(self):
        columns = set(Shipment.__table__.columns.keys())
        assert "id" in columns
