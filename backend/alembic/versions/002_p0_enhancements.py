"""
P0 Enhancements - Add confidence fields, QR codes, and performance indexes
Revision ID: 002_p0_enhancements
Revises: 001_initial_schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_p0_enhancements'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add confidence and QR fields to assessments
    op.add_column('assessments', sa.Column('confidence_p10', sa.Float))
    op.add_column('assessments', sa.Column('confidence_p50', sa.Float))
    op.add_column('assessments', sa.Column('confidence_p90', sa.Float))
    op.add_column('assessments', sa.Column('data_sources', postgresql.JSONB))
    op.add_column('assessments', sa.Column('qr_verification_code', sa.String(100), unique=True))
    op.add_column('assessments', sa.Column('pdf_url', sa.String(500)))
    op.add_column('assessments', sa.Column('scenarios_data', postgresql.JSONB))
    
    # Create index on QR code for fast verification lookups
    op.create_index('ix_assessments_qr_code', 'assessments', ['qr_verification_code'])
    
    # Add fraud_score column to verifications if not exists
    # (Already in schema but adding for completeness)
    
    # Performance indexes for common queries
    op.create_index('ix_verifications_status', 'verifications', ['status'])
    op.create_index('ix_verifications_project_id', 'verifications', ['project_id'])
    
    # Auction/Bid indexes (if tables exist from 001)
    # Note: 001_initial_schema has bids table
    op.create_index('ix_bids_project_id', 'bids', ['project_id'])
    op.create_index('ix_bids_installer_id', 'bids', ['installer_id'])
    op.create_index('ix_bids_status', 'bids', ['status'])
    
    # GIN indexes for JSONB columns for faster JSON queries
    op.create_index('ix_assessments_system_recommendations_gin', 'assessments', ['system_recommendations'], postgresql_using='gin')
    op.create_index('ix_assessments_data_sources_gin', 'assessments', ['data_sources'], postgresql_using='gin')
    op.create_index('ix_assessments_scenarios_gin', 'assessments', ['scenarios_data'], postgresql_using='gin')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_assessments_scenarios_gin', 'assessments')
    op.drop_index('ix_assessments_data_sources_gin', 'assessments')
    op.drop_index('ix_assessments_system_recommendations_gin', 'assessments')
    op.drop_index('ix_bids_status', 'bids')
    op.drop_index('ix_bids_installer_id', 'bids')
    op.drop_index('ix_bids_project_id', 'bids')
    op.drop_index('ix_verifications_project_id', 'verifications')
    op.drop_index('ix_verifications_status', 'verifications')
    op.drop_index('ix_assessments_qr_code', 'assessments')
    
    # Drop columns
    op.drop_column('assessments', 'scenarios_data')
    op.drop_column('assessments', 'pdf_url')
    op.drop_column('assessments', 'qr_verification_code')
    op.drop_column('assessments', 'data_sources')
    op.drop_column('assessments', 'confidence_p90')
    op.drop_column('assessments', 'confidence_p50')
    op.drop_column('assessments', 'confidence_p10')
