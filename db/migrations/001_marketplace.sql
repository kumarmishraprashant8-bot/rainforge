-- RainForge Marketplace Database Migration
-- Version: 001_marketplace_tables
-- Execute with: psql -d rainforge -f 001_marketplace.sql

-- ============================================================
-- INSTALLER ENHANCEMENTS
-- ============================================================

ALTER TABLE installers ADD COLUMN IF NOT EXISTS rpi_score FLOAT DEFAULT 50.0;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS rpi_components JSONB DEFAULT '{}';
ALTER TABLE installers ADD COLUMN IF NOT EXISTS cert_level VARCHAR(50) DEFAULT 'basic';
ALTER TABLE installers ADD COLUMN IF NOT EXISTS capacity_estimate INT DEFAULT 10;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS is_blacklisted BOOLEAN DEFAULT FALSE;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS blacklist_reason TEXT;
ALTER TABLE installers ADD COLUMN IF NOT EXISTS sla_compliance_pct FLOAT DEFAULT 90.0;

-- ============================================================
-- JOBS ENHANCEMENTS
-- ============================================================

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS allocation_mode VARCHAR(50) DEFAULT 'user_choice';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS bid_status VARCHAR(50) DEFAULT 'closed';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS assigned_installer_id INT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS allocation_score FLOAT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS allocation_reason TEXT;

-- ============================================================
-- BIDS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS bids (
    id VARCHAR(50) PRIMARY KEY,
    job_id INT NOT NULL,
    installer_id INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    timeline_days INT NOT NULL,
    warranty_months INT DEFAULT 12,
    notes TEXT,
    score FLOAT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bids_job_id ON bids(job_id);
CREATE INDEX IF NOT EXISTS idx_bids_installer_id ON bids(installer_id);
CREATE INDEX IF NOT EXISTS idx_bids_status ON bids(status);

-- ============================================================
-- PAYMENTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(50) PRIMARY KEY,
    job_id INT NOT NULL UNIQUE,
    total_amount DECIMAL(12,2) NOT NULL,
    escrow_amount DECIMAL(12,2) DEFAULT 0,
    released_amount DECIMAL(12,2) DEFAULT 0,
    provider VARCHAR(50) DEFAULT 'mock',
    provider_ref VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payments_job_id ON payments(job_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- ============================================================
-- MILESTONES TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS milestones (
    id VARCHAR(50) PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL REFERENCES payments(id),
    name VARCHAR(100) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    sequence INT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    released_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_milestones_payment_id ON milestones(payment_id);

-- ============================================================
-- VERIFICATIONS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS verifications (
    id VARCHAR(50) PRIMARY KEY,
    job_id INT NOT NULL,
    installer_id INT NOT NULL,
    photo_url TEXT NOT NULL,
    photo_hash VARCHAR(64),
    geo_lat FLOAT NOT NULL,
    geo_lng FLOAT NOT NULL,
    expected_lat FLOAT,
    expected_lng FLOAT,
    geo_distance_m FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verifier_id INT,
    status VARCHAR(50) DEFAULT 'pending',
    fraud_flags JSONB DEFAULT '[]',
    fraud_risk_score FLOAT DEFAULT 0,
    notes TEXT,
    verifier_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verifications_job_id ON verifications(job_id);
CREATE INDEX IF NOT EXISTS idx_verifications_status ON verifications(status);
CREATE INDEX IF NOT EXISTS idx_verifications_installer_id ON verifications(installer_id);

-- ============================================================
-- AUDITS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS audits (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL,
    verification_id VARCHAR(50) REFERENCES verifications(id),
    trigger_type VARCHAR(50) NOT NULL,
    findings JSONB DEFAULT '{}',
    resolution VARCHAR(50),
    resolution_notes TEXT,
    auditor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audits_job_id ON audits(job_id);
CREATE INDEX IF NOT EXISTS idx_audits_trigger_type ON audits(trigger_type);

-- ============================================================
-- AMC PACKAGES TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS amc_packages (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    price_yearly DECIMAL(10,2) NOT NULL,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default packages
INSERT INTO amc_packages (id, name, tier, price_yearly, features) VALUES
('AMC-BRONZE', 'Bronze Care', 'bronze', 2500, '["Annual inspection", "Filter replacement", "Basic cleaning", "Phone support"]'),
('AMC-SILVER', 'Silver Shield', 'silver', 5000, '["Bi-annual inspection", "Filter replacement", "Tank cleaning", "Minor repairs", "Priority support", "Water quality testing"]'),
('AMC-GOLD', 'Gold Premium', 'gold', 8500, '["Quarterly inspection", "All replacements", "Complete maintenance", "All repairs", "24/7 emergency", "Water quality testing", "Performance guarantee", "Insurance coverage"]')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- WARRANTIES TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS warranties (
    id VARCHAR(50) PRIMARY KEY,
    job_id INT NOT NULL,
    amc_package_id VARCHAR(50) REFERENCES amc_packages(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    auto_renew BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_warranties_job_id ON warranties(job_id);

-- ============================================================
-- OUTCOME CONTRACTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS outcome_contracts (
    id VARCHAR(50) PRIMARY KEY,
    job_id INT NOT NULL UNIQUE,
    target_capture_liters INT NOT NULL,
    actual_capture_liters INT DEFAULT 0,
    monitoring_start DATE NOT NULL,
    monitoring_end DATE NOT NULL,
    achievement_pct FLOAT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    final_payment_released BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_outcome_contracts_job_id ON outcome_contracts(job_id);
CREATE INDEX IF NOT EXISTS idx_outcome_contracts_status ON outcome_contracts(status);

-- ============================================================
-- RPI HISTORY TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS rpi_history (
    id SERIAL PRIMARY KEY,
    installer_id INT NOT NULL,
    rpi_score FLOAT NOT NULL,
    components JSONB NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rpi_history_installer_id ON rpi_history(installer_id);

-- ============================================================
-- CERTIFICATIONS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS certifications (
    id SERIAL PRIMARY KEY,
    installer_id INT NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    quiz_score INT NOT NULL,
    passed BOOLEAN NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_certifications_installer_id ON certifications(installer_id);

-- ============================================================
-- DEMO DATA
-- ============================================================

-- This would be populated by seed script
-- See: db/seed_demo_data.sql
