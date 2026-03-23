"""
Create shipment_assignments and shipment_locations tables
"""
from alembic import op
import sqlalchemy as sa

revision = '20260206_dispatch_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'shipment_assignments',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('shipment_id', sa.Integer, sa.ForeignKey('shipments.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('driver_user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('dispatcher_user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, default='active'),
        sa.Column('notes', sa.String(512), nullable=True),
        sa.Column('eta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        'shipment_locations',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('shipment_id', sa.Integer, sa.ForeignKey('shipments.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('driver_user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('lat', sa.Float, nullable=False),
        sa.Column('lng', sa.Float, nullable=False),
        sa.Column('accuracy', sa.Float, nullable=True),
        sa.Column('speed', sa.Float, nullable=True),
        sa.Column('heading', sa.Float, nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )

def downgrade():
    op.drop_table('shipment_assignments')
    op.drop_table('shipment_locations')
