-- RainForge PostgreSQL Initialization
-- PostGIS extension and base schema

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create schema
CREATE SCHEMA IF NOT EXISTS rainforge;

-- Grant permissions
GRANT ALL ON SCHEMA rainforge TO rainforge;
