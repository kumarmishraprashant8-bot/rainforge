"""
Database Performance Indexes Migration
Optimized indexes for common query patterns
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002_performance_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance-optimized indexes."""
    
    # ===========================================
    # PROJECTS TABLE INDEXES
    # ===========================================
    
    # Composite index for project listings by user and status
    op.create_index(
        'ix_projects_user_status',
        'projects',
        ['user_id', 'status', 'created_at'],
        postgresql_using='btree'
    )
    
    # Geographic index for location-based queries
    op.create_index(
        'ix_projects_location',
        'projects',
        ['state', 'district', 'city'],
        postgresql_using='btree'
    )
    
    # Full-text search index for project search
    op.execute("""
        CREATE INDEX ix_projects_search ON projects 
        USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(address, '')))
    """)
    
    # Spatial index for PostGIS geometry
    op.execute("""
        CREATE INDEX ix_projects_geometry ON projects 
        USING gist(geometry) WHERE geometry IS NOT NULL
    """)
    
    # ===========================================
    # ASSESSMENTS TABLE INDEXES
    # ===========================================
    
    # Index for assessment by project
    op.create_index(
        'ix_assessments_project',
        'assessments',
        ['project_id', 'created_at'],
        postgresql_using='btree'
    )
    
    # Index for water potential filtering
    op.create_index(
        'ix_assessments_water_potential',
        'assessments',
        ['annual_collection_liters'],
        postgresql_using='btree'
    )
    
    # ===========================================
    # SENSOR READINGS TABLE INDEXES
    # ===========================================
    
    # Time-series index for sensor data (important for monitoring)
    op.create_index(
        'ix_readings_sensor_time',
        'sensor_readings',
        ['sensor_id', 'recorded_at'],
        postgresql_using='btree'
    )
    
    # Partial index for recent readings only
    op.execute("""
        CREATE INDEX ix_readings_recent ON sensor_readings (sensor_id, recorded_at)
        WHERE recorded_at > NOW() - INTERVAL '30 days'
    """)
    
    # ===========================================
    # INSTALLERS TABLE INDEXES
    # ===========================================
    
    # Index for installer search by area and rating
    op.create_index(
        'ix_installers_area_rating',
        'installers',
        ['service_area', 'rating', 'is_verified'],
        postgresql_using='btree'
    )
    
    # Full-text search for installer name/specialization
    op.execute("""
        CREATE INDEX ix_installers_search ON installers 
        USING gin(to_tsvector('english', coalesce(company_name, '') || ' ' || coalesce(specializations, '')))
    """)
    
    # ===========================================
    # PAYMENTS TABLE INDEXES
    # ===========================================
    
    # Index for payment lookups
    op.create_index(
        'ix_payments_project_status',
        'payments',
        ['project_id', 'status', 'created_at'],
        postgresql_using='btree'
    )
    
    # Index for escrow tracking
    op.create_index(
        'ix_payments_escrow',
        'payments',
        ['escrow_status', 'release_date'],
        postgresql_using='btree',
        postgresql_where='escrow_status IS NOT NULL'
    )
    
    # ===========================================
    # VERIFICATION PHOTOS TABLE INDEXES
    # ===========================================
    
    # Index for photo verification queue
    op.create_index(
        'ix_photos_verification_queue',
        'verification_photos',
        ['verification_status', 'uploaded_at'],
        postgresql_using='btree'
    )
    
    # ===========================================
    # AUDIT LOGS TABLE INDEXES
    # ===========================================
    
    # Index for audit trail queries
    op.create_index(
        'ix_audit_entity',
        'audit_logs',
        ['entity_type', 'entity_id', 'created_at'],
        postgresql_using='btree'
    )
    
    # Index for user activity
    op.create_index(
        'ix_audit_user',
        'audit_logs',
        ['user_id', 'action', 'created_at'],
        postgresql_using='btree'
    )
    
    # ===========================================
    # NOTIFICATIONS TABLE INDEXES
    # ===========================================
    
    # Index for unread notifications
    op.create_index(
        'ix_notifications_unread',
        'notifications',
        ['user_id', 'created_at'],
        postgresql_using='btree',
        postgresql_where='read_at IS NULL'
    )
    
    # ===========================================
    # USERS TABLE INDEXES
    # ===========================================
    
    # Unique index on email (case-insensitive)
    op.execute("""
        CREATE UNIQUE INDEX ix_users_email_lower ON users (LOWER(email))
    """)
    
    # Index for phone lookup
    op.create_index(
        'ix_users_phone',
        'users',
        ['phone'],
        postgresql_using='btree',
        unique=True
    )


def downgrade():
    """Remove all performance indexes."""
    
    # Projects
    op.drop_index('ix_projects_user_status')
    op.drop_index('ix_projects_location')
    op.drop_index('ix_projects_search')
    op.drop_index('ix_projects_geometry')
    
    # Assessments
    op.drop_index('ix_assessments_project')
    op.drop_index('ix_assessments_water_potential')
    
    # Sensor readings
    op.drop_index('ix_readings_sensor_time')
    op.drop_index('ix_readings_recent')
    
    # Installers
    op.drop_index('ix_installers_area_rating')
    op.drop_index('ix_installers_search')
    
    # Payments
    op.drop_index('ix_payments_project_status')
    op.drop_index('ix_payments_escrow')
    
    # Verification photos
    op.drop_index('ix_photos_verification_queue')
    
    # Audit logs
    op.drop_index('ix_audit_entity')
    op.drop_index('ix_audit_user')
    
    # Notifications
    op.drop_index('ix_notifications_unread')
    
    # Users
    op.drop_index('ix_users_email_lower')
    op.drop_index('ix_users_phone')
