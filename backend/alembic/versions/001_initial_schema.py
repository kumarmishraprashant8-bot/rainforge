"""
Alembic Database Migrations
Initial migration for RainForge schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==================== USERS & AUTH ====================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), unique=True),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, default='user'),
        sa.Column('tenant_id', sa.String(50), default='default'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('preferences', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_phone', 'users', ['phone'])
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])

    # OAuth accounts
    op.create_table(
        'oauth_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user')
    )

    # ==================== PROJECTS ====================
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tenant_id', sa.String(50), default='default'),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(100)),
        sa.Column('pin_code', sa.String(10)),
        sa.Column('latitude', sa.Float),
        sa.Column('longitude', sa.Float),
        sa.Column('building_type', sa.String(50)),
        sa.Column('roof_area_sqm', sa.Float),
        sa.Column('roof_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('subsidy_eligible', sa.Boolean, default=False),
        sa.Column('subsidy_amount', sa.Float),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_city', 'projects', ['city'])

    # ==================== ASSESSMENTS ====================
    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('annual_rainfall_mm', sa.Float),
        sa.Column('catchment_area_sqm', sa.Float),
        sa.Column('runoff_coefficient', sa.Float),
        sa.Column('yearly_yield_liters', sa.Float),
        sa.Column('recommended_tank_liters', sa.Float),
        sa.Column('estimated_cost_min', sa.Float),
        sa.Column('estimated_cost_max', sa.Float),
        sa.Column('roi_years', sa.Float),
        sa.Column('carbon_offset_kg', sa.Float),
        sa.Column('system_recommendations', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # ==================== INSTALLATIONS ====================
    op.create_table(
        'installations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('installer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('bid_id', sa.Integer),
        sa.Column('tank_capacity_liters', sa.Float),
        sa.Column('tank_type', sa.String(50)),
        sa.Column('filter_type', sa.String(50)),
        sa.Column('pump_hp', sa.Float),
        sa.Column('components', postgresql.JSONB),
        sa.Column('installation_date', sa.Date),
        sa.Column('completion_date', sa.Date),
        sa.Column('warranty_months', sa.Integer),
        sa.Column('total_cost', sa.Float),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )

    # ==================== VERIFICATIONS ====================
    op.create_table(
        'verifications',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('submission_type', sa.String(50)),  # pre, during, post, periodic
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('submitted_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Column('notes', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('fraud_score', sa.Float),
        sa.Column('metadata', postgresql.JSONB),
    )

    # Verification photos
    op.create_table(
        'verification_photos',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('verification_id', sa.Integer, sa.ForeignKey('verifications.id'), nullable=False),
        sa.Column('photo_type', sa.String(50)),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500)),
        sa.Column('perceptual_hash', sa.String(64)),
        sa.Column('cv_analysis', postgresql.JSONB),
        sa.Column('latitude', sa.Float),
        sa.Column('longitude', sa.Float),
        sa.Column('captured_at', sa.DateTime),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_verification_photos_hash', 'verification_photos', ['perceptual_hash'])

    # ==================== MARKETPLACE ====================
    op.create_table(
        'installers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('license_number', sa.String(100)),
        sa.Column('gst_number', sa.String(20)),
        sa.Column('pan_number', sa.String(20)),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('verification_date', sa.DateTime),
        sa.Column('rating', sa.Float),
        sa.Column('review_count', sa.Integer, default=0),
        sa.Column('projects_completed', sa.Integer, default=0),
        sa.Column('service_areas', postgresql.ARRAY(sa.String)),
        sa.Column('specializations', postgresql.ARRAY(sa.String)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'bids',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('installer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('installers.id'), nullable=False),
        sa.Column('bid_amount', sa.Float, nullable=False),
        sa.Column('timeline_days', sa.Integer),
        sa.Column('warranty_months', sa.Integer),
        sa.Column('scope_of_work', sa.Text),
        sa.Column('materials_breakdown', postgresql.JSONB),
        sa.Column('status', sa.String(50), default='submitted'),
        sa.Column('is_awarded', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )

    # ==================== PAYMENTS ====================
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('payment_type', sa.String(50)),  # subsidy, escrow, refund
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('gateway', sa.String(50)),
        sa.Column('gateway_order_id', sa.String(100)),
        sa.Column('gateway_payment_id', sa.String(100)),
        sa.Column('utr_number', sa.String(50)),
        sa.Column('bank_reference', sa.String(100)),
        sa.Column('failure_reason', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
    )
    op.create_index('ix_payments_project_id', 'payments', ['project_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])

    # ==================== IOT / SENSORS ====================
    op.create_table(
        'sensors',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('project_id', sa.Integer, sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('sensor_type', sa.String(50), nullable=False),
        sa.Column('protocol', sa.String(20)),  # mqtt, lorawan, http
        sa.Column('dev_eui', sa.String(20)),  # For LoRaWAN
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('last_reading', sa.Float),
        sa.Column('last_reading_at', sa.DateTime),
        sa.Column('battery_percent', sa.Float),
        sa.Column('firmware_version', sa.String(20)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('sensor_id', sa.String(50), sa.ForeignKey('sensors.id'), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('unit', sa.String(20)),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('metadata', postgresql.JSONB),
    )
    op.create_index('ix_sensor_readings_sensor_timestamp', 'sensor_readings', ['sensor_id', 'timestamp'])

    # ==================== NOTIFICATIONS ====================
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text),
        sa.Column('data', postgresql.JSONB),
        sa.Column('channels', postgresql.ARRAY(sa.String)),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('sent_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime),
    )
    op.create_index('ix_notifications_user_unread', 'notifications', ['user_id', 'is_read'])

    # ==================== AUDIT LOG ====================
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('level', sa.String(20), default='info'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_email', sa.String(255)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('changes', postgresql.JSONB),
        sa.Column('metadata', postgresql.JSONB),
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

    # ==================== TENANTS ====================
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255)),
        sa.Column('type', sa.String(50)),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('config', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    tables = [
        'tenants',
        'audit_logs',
        'notifications',
        'sensor_readings',
        'sensors',
        'payments',
        'bids',
        'installers',
        'verification_photos',
        'verifications',
        'installations',
        'assessments',
        'projects',
        'oauth_accounts',
        'users',
    ]
    
    for table in tables:
        op.drop_table(table)
