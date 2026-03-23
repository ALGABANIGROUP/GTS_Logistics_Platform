"""merge admin/email heads into a single head

Revision ID: 7b9c1a2d3e4f
Revises: 2387024149f8, e7b1c4d9a2f0
Create Date: 2025-12-29
"""

from __future__ import annotations

from typing import Sequence, Union


revision: str = "7b9c1a2d3e4f"
down_revision: Union[str, Sequence[str], None] = ("2387024149f8", "e7b1c4d9a2f0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # merge-only revision
    pass


def downgrade() -> None:
    # merge-only revision
    pass
