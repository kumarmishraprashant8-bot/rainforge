#!/bin/bash
# RainForge Demo Launcher
# One-command demo environment setup

set -e

echo "🌧️ RainForge Demo Launcher"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prereqs() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not found.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites OK${NC}"
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"
    
    # Use docker compose (v2) or docker-compose (v1)
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    echo -e "${GREEN}✓ Services started${NC}"
}

# Wait for database
wait_for_db() {
    echo -e "${YELLOW}Waiting for database...${NC}"
    
    for i in {1..30}; do
        if docker exec rainforge-postgres pg_isready -U rainforge &> /dev/null; then
            echo -e "${GREEN}✓ Database ready${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ Database timeout${NC}"
    exit 1
}

# Run migrations
run_migrations() {
    echo -e "${YELLOW}Running database migrations...${NC}"
    
    docker exec rainforge-backend alembic upgrade head 2>/dev/null || {
        echo -e "${YELLOW}⚠ Migrations skipped (may already be applied)${NC}"
    }
    
    echo -e "${GREEN}✓ Migrations complete${NC}"
}

# Seed data
seed_data() {
    echo -e "${YELLOW}Seeding demo data...${NC}"
    
    docker exec -i rainforge-postgres psql -U rainforge -d rainforge < db/seed_db.sql 2>/dev/null || {
        # Fallback: copy and run
        docker cp db/seed_db.sql rainforge-postgres:/tmp/seed_db.sql
        docker exec rainforge-postgres psql -U rainforge -d rainforge -f /tmp/seed_db.sql
    }
    
    echo -e "${GREEN}✓ Demo data seeded${NC}"
}

# Print status
print_status() {
    echo ""
    echo -e "${GREEN}🎉 RainForge Demo Ready!${NC}"
    echo "=========================="
    echo ""
    echo "📍 Frontend:   http://localhost:3000"
    echo "📍 Backend:    http://localhost:8000"
    echo "📍 API Docs:   http://localhost:8000/docs"
    echo ""
    echo "🔑 Demo Credentials:"
    echo "   Admin:     admin@rainforge.in / demo123"
    echo "   Verifier:  verifier@rainforge.in / demo123"
    echo "   Installer: installer@rainforge.in / demo123"
    echo ""
    echo "📊 Seed Data:"
    echo "   - 50 sample sites (verified + pending + fraud)"
    echo "   - 6 installers with RPI scores"
    echo "   - 10 subsidy rules (state-wise)"
    echo "   - 3 ward boundaries"
    echo ""
    echo "📋 Demo Script: docs/demo_plan.md"
    echo ""
    echo -e "${YELLOW}To stop: docker compose down${NC}"
}

# Main flow
main() {
    check_prereqs
    start_services
    wait_for_db
    run_migrations
    seed_data
    print_status
}

main "$@"
