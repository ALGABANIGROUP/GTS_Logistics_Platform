#!/usr/bin/env python
"""
Alembic Migration - Add Freight Broker Tables

Run this migration to create the broker_commission_tiers, 
broker_commissions, and invoices_enhanced tables.

Usage:
  alembic revision --autogenerate -m "Add freight broker tables"
  alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Create broker commission tables"""
    
    # Commission Tiers table
    op.create_table(
        'broker_commission_tiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('shipment_type', sa.String(50), nullable=False),
        sa.Column('commission_percentage', sa.Float(), nullable=False),
        sa.Column('minimum_commission', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('maximum_commission', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_broker_commission_tiers_id', 'broker_commission_tiers', ['id'])
    
    # Broker Commissions table
    op.create_table(
        'broker_commissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('shipment_number', sa.String(50), nullable=False),
        sa.Column('client_invoice_amount', sa.Float(), nullable=False),
        sa.Column('carrier_cost', sa.Float(), nullable=False),
        sa.Column('commission_tier_id', sa.Integer(), sa.ForeignKey('broker_commission_tiers.id'), nullable=True),
        sa.Column('commission_percentage', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('commission_amount', sa.Float(), nullable=False),
        sa.Column('gross_profit', sa.Float(), nullable=False),
        sa.Column('net_profit', sa.Float(), nullable=False),
        sa.Column('profit_margin_percentage', sa.Float(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('shipment_date', sa.DateTime(), nullable=True),
        sa.Column('delivery_date', sa.DateTime(), nullable=True),
        sa.Column('commission_payment_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_broker_commissions_id', 'broker_commissions', ['id'])
    op.create_index('ix_broker_commissions_shipment_id', 'broker_commissions', ['shipment_id'])
    
    # Enhanced Invoices table
    op.create_table(
        'invoices_enhanced',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(100), nullable=False, unique=True),
        sa.Column('invoice_type', sa.String(50), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('shipment_id', sa.Integer(), nullable=True),
        sa.Column('shipment_number', sa.String(50), nullable=True),
        sa.Column('from_party', sa.String(200), nullable=True),
        sa.Column('to_party', sa.String(200), nullable=True),
        sa.Column('amount_usd', sa.Float(), nullable=False),
        sa.Column('commission_percentage', sa.Float(), nullable=True),
        sa.Column('commission_amount', sa.Float(), nullable=True),
        sa.Column('carrier_cost', sa.Float(), nullable=True),
        sa.Column('profit_margin', sa.Float(), nullable=True),
        sa.Column('profit_margin_percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('currency', sa.String(10), nullable=False, server_default='USD'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invoices_enhanced_id', 'invoices_enhanced', ['id'])
    op.create_index('ix_invoices_enhanced_number', 'invoices_enhanced', ['number'])
    op.create_index('ix_invoices_enhanced_shipment_id', 'invoices_enhanced', ['shipment_id'])


def downgrade():
    """Drop broker commission tables"""
    op.drop_index('ix_invoices_enhanced_shipment_id', 'invoices_enhanced')
    op.drop_index('ix_invoices_enhanced_number', 'invoices_enhanced')
    op.drop_index('ix_invoices_enhanced_id', 'invoices_enhanced')
    op.drop_table('invoices_enhanced')
    
    op.drop_index('ix_broker_commissions_shipment_id', 'broker_commissions')
    op.drop_index('ix_broker_commissions_id', 'broker_commissions')
    op.drop_table('broker_commissions')
    
    op.drop_index('ix_broker_commission_tiers_id', 'broker_commission_tiers')
    op.drop_table('broker_commission_tiers')
