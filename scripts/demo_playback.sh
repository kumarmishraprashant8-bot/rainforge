#!/bin/bash
# RainForge Demo Playback Script
# Runs through complete demo flow using curl

set -e

API_BASE="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       RainForge Demo Playback Script         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# Health check
echo -e "${GREEN}1. Health Check...${NC}"
curl -s ${API_BASE}/health | jq .
echo ""

# Create Assessment
echo -e "${GREEN}2. Creating Assessment...${NC}"
ASSESS_RESPONSE=$(curl -s -X POST ${API_BASE}/assess \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "DEMO-PLAY-001",
    "address": "Municipal School Sector 5, Rohini, Delhi",
    "lat": 28.7041,
    "lng": 77.1025,
    "roof_area_sqm": 250,
    "roof_material": "concrete",
    "demand_l_per_day": 400,
    "floors": 2,
    "people": 150,
    "state": "Delhi",
    "city": "New Delhi"
  }')
echo $ASSESS_RESPONSE | jq .
ASSESSMENT_ID=$(echo $ASSESS_RESPONSE | jq -r '.assessment_id')
VERIFY_URL=$(echo $ASSESS_RESPONSE | jq -r '.verify_url')
echo ""

# Verify Assessment via QR
echo -e "${GREEN}3. Verifying Assessment via QR Code...${NC}"
VERIFY_CODE=$(echo $VERIFY_URL | grep -oP 'verify/\K.*')
curl -s ${API_BASE}/verify/${VERIFY_CODE} | jq .
echo ""

# List Installers
echo -e "${GREEN}4. Listing Available Installers...${NC}"
curl -s "${API_BASE}/installers?min_rpi=70" | jq '.installers[:3]'
echo ""

# Run Allocation
echo -e "${GREEN}5. Running Gov-Optimized Allocation...${NC}"
curl -s -X POST ${API_BASE}/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["JOB-DEMO-001"],
    "mode": "gov_optimized"
  }' | jq .
echo ""

# Submit Telemetry
echo -e "${GREEN}6. Submitting Tank Telemetry...${NC}"
curl -s -X POST ${API_BASE}/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TANK-DEMO-001",
    "project_id": 1,
    "tank_level_liters": 5700,
    "battery_pct": 87.5,
    "signal_rssi": -67
  }' | jq .
echo ""

# Get Monitoring Data
echo -e "${GREEN}7. Fetching Monitoring Data...${NC}"
curl -s "${API_BASE}/monitoring/1?hours=24" | jq '{current_level, days_until_empty, alerts}'
echo ""

# Public Dashboard
echo -e "${GREEN}8. Public Transparency Dashboard...${NC}"
curl -s ${API_BASE}/public/dashboard | jq '.summary'
echo ""

# Batch Assessment (if sample file exists)
if [ -f "backend/seed_data/sample_bulk.csv" ]; then
  echo -e "${GREEN}9. Running Batch Assessment...${NC}"
  curl -s -X POST ${API_BASE}/batch/assess \
    -F "file=@backend/seed_data/sample_bulk.csv" \
    -F "scenario=cost_optimized" | jq '{batch_id, status, total_rows, summary}'
  echo ""
fi

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Demo Playback Complete!             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
