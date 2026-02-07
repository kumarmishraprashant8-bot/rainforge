-- RainForge Master Migration - V2 Core Tables
-- Run after init.sql to add new government-grade features

-- ============================================================
-- ORGANIZATIONS & ENHANCED USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'government', -- government, commercial, residential
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    state VARCHAR(100),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add org_id to users if not exists
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='org_id') THEN
        ALTER TABLE users ADD COLUMN org_id INTEGER REFERENCES organizations(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='password_hash') THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
    END IF;
END $$;

-- ============================================================
-- PROJECTS & ASSESSMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    lat DECIMAL(10, 6),
    lng DECIMAL(10, 6),
    roof_geom geometry(Polygon, 4326),
    state VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    ward VARCHAR(100),
    building_type VARCHAR(50) DEFAULT 'residential', -- residential, commercial, industrial, government
    floors INTEGER DEFAULT 1,
    people INTEGER,
    monthly_water_bill DECIMAL(10, 2),
    existing_tank_l INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- quick, complete, bulk
    scenario VARCHAR(50) DEFAULT 'cost_optimized', -- cost_optimized, max_capture, dry_season
    parameters_json JSONB NOT NULL,
    result_json JSONB,
    ruleset_id INTEGER,
    annual_yield_l DECIMAL(15, 2),
    tank_recommendation_l DECIMAL(15, 2),
    estimated_cost DECIMAL(15, 2),
    subsidy_amount DECIMAL(15, 2),
    net_cost DECIMAL(15, 2),
    roi_years DECIMAL(5, 2),
    reliability_pct DECIMAL(5, 2),
    co2_offset_kg DECIMAL(10, 2),
    pdf_url TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ============================================================
-- BULK PROCESSING
-- ============================================================

CREATE TABLE IF NOT EXISTS bulk_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id INTEGER REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    job_type VARCHAR(50) DEFAULT 'assessment', -- assessment, verification
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    rows_total INTEGER DEFAULT 0,
    rows_processed INTEGER DEFAULT 0,
    rows_success INTEGER DEFAULT 0,
    rows_failed INTEGER DEFAULT 0,
    input_file_url TEXT,
    output_zip_url TEXT,
    error_sample_url TEXT,
    weight_config JSONB,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bulk_job_rows (
    id SERIAL PRIMARY KEY,
    bulk_job_id UUID REFERENCES bulk_jobs(id) ON DELETE CASCADE,
    row_number INTEGER,
    site_id VARCHAR(255),
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    assessment_id INTEGER REFERENCES assessments(id),
    processed_at TIMESTAMP
);

-- ============================================================
-- MONITORING DATA (for IoT sensors)
-- ============================================================

CREATE TABLE IF NOT EXISTS sensors (
    id VARCHAR(100) PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    sensor_type VARCHAR(50) DEFAULT 'tank_level', -- tank_level, flow_meter, quality
    name VARCHAR(255),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    api_key_hash VARCHAR(255),
    last_seen TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitoring_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(100) REFERENCES sensors(id),
    project_id INTEGER REFERENCES projects(id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    level_percent DECIMAL(5, 2),
    level_volume_l DECIMAL(15, 2),
    flow_rate_lpm DECIMAL(10, 2),
    battery_pct DECIMAL(5, 2),
    ph_level DECIMAL(4, 2),
    turbidity_ntu DECIMAL(8, 2),
    temperature_c DECIMAL(5, 2),
    raw_data JSONB
);

-- Create hypertable for time-series data if using TimescaleDB
-- SELECT create_hypertable('monitoring_data', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_monitoring_sensor_time ON monitoring_data(sensor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_project_time ON monitoring_data(project_id, timestamp DESC);

-- ============================================================
-- ENHANCED VERIFICATIONS
-- ============================================================

ALTER TABLE verifications ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS photos_json JSONB;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS exif_data_json JSONB;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS ai_confidence DECIMAL(5, 4);
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS ai_predictions JSONB;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS reviewer_id UUID REFERENCES users(id);
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS audit_hash VARCHAR(64);
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS signature TEXT;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;

-- ============================================================
-- MARKETPLACE ENHANCEMENTS
-- ============================================================

ALTER TABLE installers ADD COLUMN IF NOT EXISTS org_id INTEGER REFERENCES organizations(id);
ALTER TABLE installers ADD COLUMN IF NOT EXISTS slots_available INTEGER DEFAULT 10;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS price_per_kl DECIMAL(10, 2);
ALTER TABLE installers ADD COLUMN IF NOT EXISTS sla_days INTEGER DEFAULT 30;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS rating DECIMAL(3, 2) DEFAULT 4.0;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS total_jobs INTEGER DEFAULT 0;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS completed_jobs INTEGER DEFAULT 0;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS service_radius_km INTEGER DEFAULT 50;

CREATE TABLE IF NOT EXISTS marketplace_allocations (
    id SERIAL PRIMARY KEY,
    bulk_job_id UUID REFERENCES bulk_jobs(id),
    project_id INTEGER REFERENCES projects(id),
    installer_id INTEGER REFERENCES installers(id),
    score DECIMAL(5, 4),
    rank INTEGER,
    score_breakdown JSONB,
    status VARCHAR(50) DEFAULT 'proposed',
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- SUBSIDY RULES
-- ============================================================

CREATE TABLE IF NOT EXISTS subsidy_rules (
    id SERIAL PRIMARY KEY,
    state VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    scheme_code VARCHAR(50),
    subsidy_type VARCHAR(50) DEFAULT 'percentage', -- percentage, fixed, tiered
    subsidy_percent DECIMAL(5, 2),
    max_amount DECIMAL(15, 2),
    min_roof_area_sqm DECIMAL(10, 2),
    max_roof_area_sqm DECIMAL(10, 2),
    eligibility_json JSONB,
    documentation_required TEXT[],
    valid_from DATE,
    valid_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- AUDIT LOG (Append-only, immutable)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    actor_id UUID REFERENCES users(id),
    actor_type VARCHAR(50) DEFAULT 'user',
    data_before JSONB,
    data_after JSONB,
    data_hash VARCHAR(64),
    signature TEXT,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp DESC);

-- ============================================================
-- FILE STORAGE TRACKING
-- ============================================================

CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bucket VARCHAR(100) NOT NULL,
    key VARCHAR(500) NOT NULL,
    original_name VARCHAR(255),
    mime_type VARCHAR(100),
    size_bytes BIGINT,
    checksum_sha256 VARCHAR(64),
    uploaded_by UUID REFERENCES users(id),
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_files_entity ON files(entity_type, entity_id);

-- ============================================================
-- RAINFALL DATA CACHE
-- ============================================================

CREATE TABLE IF NOT EXISTS rainfall_data (
    id SERIAL PRIMARY KEY,
    lat DECIMAL(10, 6) NOT NULL,
    lng DECIMAL(10, 6) NOT NULL,
    grid_cell VARCHAR(50),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    rainfall_mm DECIMAL(8, 2) NOT NULL,
    source VARCHAR(50) DEFAULT 'imd', -- imd, chirps, era5, synthetic
    data_quality VARCHAR(20) DEFAULT 'measured',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(lat, lng, year, month, source)
);

CREATE INDEX IF NOT EXISTS idx_rainfall_location ON rainfall_data(lat, lng);
CREATE INDEX IF NOT EXISTS idx_rainfall_grid ON rainfall_data(grid_cell);

-- ============================================================
-- MATERIAL PRICING
-- ============================================================

CREATE TABLE IF NOT EXISTS material_prices (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    price_per_unit DECIMAL(12, 2) NOT NULL,
    vendor VARCHAR(255),
    state VARCHAR(100),
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_projects_org ON projects(org_id);
CREATE INDEX IF NOT EXISTS idx_projects_state ON projects(state);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_assessments_project ON assessments(project_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_bulk_jobs_org ON bulk_jobs(org_id);
CREATE INDEX IF NOT EXISTS idx_bulk_jobs_status ON bulk_jobs(status);

-- Spatial index for project locations
CREATE INDEX IF NOT EXISTS idx_projects_location ON projects USING GIST(roof_geom);

-- Done
SELECT 'V2 Migration completed successfully' as result;
