# RainForge Demo Guide

This guide walks you through setting up and running a complete RainForge demo, from assessment to payment release.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

## Quick Start

### 1. Start with Docker

```bash
# Clone and navigate
cd "Rain Forge"

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Services will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **MQTT**: localhost:1883

### 2. Seed Demo Data

```bash
# Run migrations and seed
docker-compose exec backend python -c "from app.seed_data import seed_demo_data; from app.models.database import SessionLocal; seed_demo_data(SessionLocal())"
```

### 3. Access the Demo

Open http://localhost:5173 in your browser.

---

## Demo Flow Walkthrough

### Step 1: Quick Assessment

1. Navigate to **Assessment** page
2. Enter:
   - **Roof Area**: 250 sqm
   - **Material**: Concrete (RCC)
   - **Address**: Municipal School Sector 5, Delhi
3. Click **Calculate**
4. View three scenarios:
   - **Cost Optimized**: Smaller tank, lower cost
   - **Max Capture**: Larger tank, maximum collection
   - **Dry Season**: Optimized for monsoon storage
5. Download **PDF Report** with QR code

### Step 2: Bulk Upload (Government Scale)

1. Navigate to **Bulk Upload**
2. Download **Sample CSV Template**
3. Upload your CSV (up to 10,000 sites)
4. Select scenario preference
5. View aggregate results

### Step 3: Find Installer (Marketplace)

1. Navigate to **Find Pros**
2. Select allocation mode:
   - **Government Optimized**: RPI-weighted + SLA compliance
   - **Equitable**: Round-robin distribution
   - **User Choice**: Select specific installer
3. Run allocation
4. View assigned installer with score breakdown

### Step 4: Competitive Bidding (Optional)

1. Open job for bidding (72-hour window)
2. Installers submit bids with:
   - Price quote
   - Timeline
   - Warranty period
3. System calculates composite score
4. Award bid to winner

### Step 5: Track Payments

1. Navigate to **Payments**
2. View escrow milestones:
   - Design Approval (10%)
   - Installation Complete (70%)
   - Final Verification (20%)
3. Track releases

### Step 6: Submit Verification

1. Installer uploads geo-tagged photos
2. System runs fraud detection:
   - EXIF GPS validation
   - Photo hash duplicate check
   - Distance verification
3. Auto-approve or flag for manual review

### Step 7: Monitor Tank

1. Navigate to **Monitoring**
2. View:
   - Real-time tank level gauge
   - 24-hour trend chart
   - Days until empty prediction
   - Overflow risk alerts

---

## API Testing with curl

### Create Assessment
```bash
curl -X POST http://localhost:8000/api/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "DEMO-001",
    "address": "Municipal School, Delhi",
    "lat": 28.6139,
    "lng": 77.2090,
    "roof_area_sqm": 200,
    "roof_material": "concrete",
    "state": "Delhi"
  }'
```

### Batch Assessment
```bash
curl -X POST http://localhost:8000/api/v1/batch/assess \
  -F "file=@backend/seed_data/sample_bulk.csv" \
  -F "scenario=cost_optimized"
```

### Run Allocation
```bash
curl -X POST http://localhost:8000/api/v1/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["JOB-001"],
    "mode": "gov_optimized"
  }'
```

### Submit Telemetry
```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TANK-001",
    "project_id": 1,
    "tank_level_liters": 4500
  }'
```

### Verify QR Code
```bash
curl http://localhost:8000/api/v1/verify/ASM-20260203-ABC123
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_PASSWORD=rainforge_dev_2026
DATABASE_URL=postgresql://rainforge:rainforge_dev_2026@localhost:5432/rainforge

# External APIs (optional - fallback to mock data)
OPENCAGE_API_KEY=your_opencage_key
OPENMETEO_API_KEY=optional

# MQTT
MQTT_BROKER_URL=mqtt://localhost:1883

# Debug
DEBUG=true
```

### Obtaining API Keys

1. **OpenCage Geocoding** (optional): https://opencagedata.com/
   - Free tier: 2,500 requests/day
   - Used for address → coordinates conversion

2. **Open-Meteo** (optional): https://open-meteo.com/
   - Free, no API key required
   - Used for rainfall data

---

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app

# Specific test suites
pytest tests/test_demo_api.py -v
pytest tests/test_fraud_detector.py -v
pytest tests/test_allocation_engine.py -v
```

---

## Troubleshooting

### Port Already in Use
```bash
docker-compose down
docker-compose up -d
```

### Database Issues
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d
```

### Frontend Not Loading
```bash
cd frontend
npm install
npm run dev
```

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API   │
│   (Vite/React)  │     │   (FastAPI)     │
└─────────────────┘     └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PostgreSQL   │     │      Redis      │     │      MQTT       │
│   + PostGIS   │     │    (Caching)    │     │   (Telemetry)   │
└───────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review OpenAPI spec: `/docs/openapi.yaml`
- Contact: support@rainforge.in
