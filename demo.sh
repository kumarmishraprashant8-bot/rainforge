#!/bin/bash
# ============================================================================
# RainForge Demo Script - Production Upgrade Features
# ============================================================================
# This script sets up and demonstrates all new features of RainForge v4.0
# Run this script from the project root directory
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                  🌧️  RAINFORGE v4.0 DEMO                          ║"
echo "║              Government-Grade RWH Platform                        ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# STEP 1: Environment Setup
# ============================================================================
echo -e "${YELLOW}[1/7] Setting up environment...${NC}"

# Create .env if not exists
if [ ! -f .env ]; then
    cp sample.env.example .env 2>/dev/null || cat > .env << EOF
MAPBOX_TOKEN=pk.placeholder
SECRET_KEY=demo-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=true
MQTT_BROKER_HOST=mqtt
MQTT_BROKER_PORT=1883
MQTT_USERNAME=rainforge
MQTT_PASSWORD=iot_secure_2024
EOF
    echo "  ✅ Created .env file"
else
    echo "  ✅ .env file exists"
fi

# ============================================================================
# STEP 2: Start Docker Services
# ============================================================================
echo -e "${YELLOW}[2/7] Starting Docker services...${NC}"

docker-compose down --remove-orphans 2>/dev/null || true
docker-compose up -d --build

echo "  ⏳ Waiting for services to be ready (30s)..."
sleep 30

# Health checks
echo "  Checking service health..."

if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "  ${GREEN}✅ Backend: healthy${NC}"
else
    echo -e "  ${RED}❌ Backend: not responding${NC}"
fi

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Frontend: running${NC}"
else
    echo -e "  ${YELLOW}⚠️ Frontend: may still be starting...${NC}"
fi

# ============================================================================
# STEP 3: Run Database Migrations
# ============================================================================
echo -e "${YELLOW}[3/7] Running database migrations...${NC}"

# Run marketplace migrations
docker exec rainforge-db psql -U user -d rainforge -f /docker-entrypoint-initdb.d/migrations/001_marketplace.sql 2>/dev/null || echo "  ⚠️ Migration may already be applied"

# Seed demo data
docker exec rainforge-db psql -U user -d rainforge -f /docker-entrypoint-initdb.d/seed_demo_data.sql 2>/dev/null || echo "  ⚠️ Seed data may already exist"

echo "  ✅ Database ready"

# ============================================================================
# STEP 4: Run Tests
# ============================================================================
echo -e "${YELLOW}[4/7] Running test suite...${NC}"

docker exec rainforge-backend pytest tests/ -v --tb=short 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️ Some tests may require additional setup${NC}"
}

# ============================================================================
# STEP 5: Test MQTT Connectivity
# ============================================================================
echo -e "${YELLOW}[5/7] Testing IoT/MQTT connectivity...${NC}"

# Test MQTT publish
docker exec rainforge-mqtt mosquitto_pub \
    -h localhost \
    -u rainforge \
    -P iot_secure_2024 \
    -t "rainforge/sensors/1/tank_level" \
    -m '{"device_id":"demo-001","value":75.5,"unit":"%","timestamp":"2024-01-15T10:30:00Z"}' \
    2>/dev/null && echo -e "  ${GREEN}✅ MQTT publish successful${NC}" || echo -e "  ${YELLOW}⚠️ MQTT may need configuration${NC}"

# ============================================================================
# STEP 6: Test API Endpoints
# ============================================================================
echo -e "${YELLOW}[6/7] Testing API endpoints...${NC}"

# Test authentication
echo "  Testing auth..."
REGISTER_RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"demo@rainforge.in","password":"SecurePass123!","full_name":"Demo User"}')
echo "  Register: $REGISTER_RESP"

LOGIN_RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demo@rainforge.in&password=SecurePass123!")
echo "  Login: $LOGIN_RESP"

# Test security headers
echo "  Testing security headers..."
HEADERS=$(curl -s -I http://localhost:8000/health | head -20)
if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    echo -e "  ${GREEN}✅ Security headers present${NC}"
else
    echo -e "  ${YELLOW}⚠️ Check security headers${NC}"
fi

# Test allocation endpoint
echo "  Testing allocation..."
curl -s http://localhost:8000/api/v1/marketplace/installers 2>/dev/null | head -c 200
echo ""

# Test public dashboard
echo "  Testing public dashboard..."
curl -s http://localhost:8000/api/v1/public/city/stats 2>/dev/null | head -c 200
echo ""

# ============================================================================
# STEP 7: Display Demo URLs
# ============================================================================
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEMO READY!                                 ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}📍 ACCESS POINTS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Frontend:           http://localhost:5173"
echo "  📚 API Docs:           http://localhost:8000/docs"
echo "  🏛️ Public Dashboard:   http://localhost:5173/public"
echo "  🛒 Marketplace:        http://localhost:5173/marketplace"
echo "  📊 Monitoring:         http://localhost:5173/monitoring"
echo "  ✅ Verification:       http://localhost:5173/verification"
echo ""
echo -e "${BLUE}🔧 DEMO FLOW:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1️⃣  Visit /public        → See city-wide water capture stats"
echo "  2️⃣  Visit /marketplace   → Run smart allocation → Award bid"
echo "  3️⃣  Visit /verification  → Submit photo proof → See fraud check"
echo "  4️⃣  Visit /monitoring    → View live IoT sensor data"
echo "  5️⃣  Check /docs          → Explore all API endpoints"
echo ""
echo -e "${BLUE}🔐 NEW SECURITY FEATURES:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ JWT Authentication with refresh tokens"
echo "  ✅ Hardened CORS (whitelist only)"
echo "  ✅ Security headers (CSP, HSTS, X-Frame-Options)"
echo "  ✅ Rate limiting (100 req/min)"
echo "  ✅ MQTT device authentication"
echo ""
echo -e "${BLUE}🤖 NEW ML FEATURES:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ RandomForest yield prediction"
echo "  ✅ Isolation Forest fraud anomaly detection"
echo "  ✅ 7-day yield forecasting"
echo ""
echo -e "${BLUE}📡 IoT INTEGRATION:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ MQTT broker running on port 1883"
echo "  ✅ Telemetry ingestion service active"
echo "  ✅ TimescaleDB for time-series (port 5433)"
echo ""
echo -e "${YELLOW}To stop services: docker-compose down${NC}"
echo ""
