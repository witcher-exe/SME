"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-14 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Company
    op.create_table(
        'company',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='BDT'),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('owner_name_hash', sa.String(64), nullable=True),
        sa.Column('tax_id_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('initial_cash_balance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('balance_sheet_snapshot', sa.JSON(), nullable=False, server_default='{}'),
    )

    # Transaction
    op.create_table(
        'transaction',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('company.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('counterparty', sa.String(255), nullable=True),
        sa.Column('raw_narration', sa.Text(), nullable=True),
        sa.Column('pii_scrubbed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_transaction_company_id', 'transaction', ['company_id'])
    op.create_index('ix_transaction_date', 'transaction', ['date'])

    # Invoice
    op.create_table(
        'invoice',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('company.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('debtor_name', sa.String(255), nullable=False),
        sa.Column('debtor_email', sa.String(255), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('issued_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='issued'),
        sa.Column('p_delay', sa.Float(), nullable=True),
        sa.Column('predicted_delay_days', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_invoice_company_id', 'invoice', ['company_id'])
    op.create_index('ix_invoice_due_date', 'invoice', ['due_date'])

    # AuditEntry
    op.create_table(
        'audit_entry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('company.id', ondelete='CASCADE'), nullable=False),
        sa.Column('block_number', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('agent_role', sa.String(50), nullable=False),
        sa.Column('tool_name', sa.String(100), nullable=False),
        sa.Column('input_hash', sa.String(64), nullable=False),
        sa.Column('output_hash', sa.String(64), nullable=False),
        sa.Column('permission_tier', sa.String(5), nullable=False),
        sa.Column('current_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('previous_hash', sa.String(64), nullable=False),
    )
    op.create_index('ix_audit_entry_company_id', 'audit_entry', ['company_id'])

    # Approval
    op.create_table(
        'approval',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('company.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('requested_by', sa.String(50), nullable=False),
        sa.Column('approved_by', sa.String(50), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('approval_token', sa.String(64), nullable=True),
        sa.Column('thread_id', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_approval_company_id', 'approval', ['company_id'])

    # PIIToken
    op.create_table(
        'pii_token',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('company.id', ondelete='CASCADE'), nullable=False),
        sa.Column('hmac_token', sa.String(50), nullable=False, unique=True),
        sa.Column('entity_category', sa.String(30), nullable=False),
        sa.Column('original_hash', sa.String(64), nullable=False),
        sa.Column('display_value', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_pii_token_company_id', 'pii_token', ['company_id'])

def downgrade() -> None:
    op.drop_table('pii_token')
    op.drop_table('approval')
    op.drop_table('audit_entry')
    op.drop_table('invoice')
    op.drop_table('transaction')
    op.drop_table('company')
