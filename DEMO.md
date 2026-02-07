# RainForge Demo Script - P0 Enhanced

**Owners**: Prashant Mishra & Ishita Parmar
**Jal Shakti Hackathon 2026**

> **🏆 All P0 Features Implemented - Ready for Demo**

This document provides step-by-step commands for judges to demo the RainForge platform.

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker Desktop installed
- Docker Compose v2.0+
- 4GB RAM available
- Ports 5173, 8000, 5432 available

### Step 1: Start All Services

```powershell
# Navigate to project directory (Windows)
cd "Rain Forge"

# Start all services
docker-compose up -d

# Wait 30-45 seconds for services to initialize
```

### Step 2: Run Migrations & Seed Data

```powershell
# Run database migrations
docker-compose exec backend alembic upgrade head

# Seed demo data
docker-compose exec backend python -c "from app.seed_data import seed_demo_data; from app.models.database import SessionLocal; db = SessionLocal(); seed_demo_data(db); db.close()"
```

### Step 3: Verify Services

```powershell
# Check all containers
docker-compose ps

# Test backend
curl http://localhost:8000/api/v1/health

# Test frontend
Start-Process "http://localhost:5173"
```

**Expected URLs**:
- 🌐 Frontend: http://localhost:5173
- 🔌 Backend API: http://localhost:8000
- 📝 API Docs: http://localhost:8000/docs

---

### Via Web UI
1. Open http://localhost:5173
2. Click **"New Assessment"**
3. Enter:
   - Address: `123 Gandhi Road, New Delhi`
   - Roof Area: `250` sqm (or draw on map)
   - Roof Material: `Concrete`
4. Click **"Run Assessment"**
5. View results with 3 scenarios

### Via API
```bash
curl -X POST http://localhost:8000/api/assessments/quick \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Gandhi Road",
    "roof_area_sqm": 250,
    "roof_material": "concrete",
    "state": "Delhi",
    "city": "New Delhi",
    "people": 5
  }'
```

**Expected Response**:
```json
{
  "project_id": 123,
  "runoff_potential_liters": 168000,
  "recommended_tank_size": 8000,
  "scenarios": [...],
  "subsidy_eligible": true,
  "estimated_subsidy_inr": 40000
}
```

### Multi-modal assessment (Feature A)
Instant assessment with input mode: **address** | **satellite-only** | **photo**. Same 1-page PDF and a confidence score.

```bash
# Address mode (full details)
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"address":"123 Gandhi Road, New Delhi","mode":"address","roof_area_sqm":120}'

# Satellite-only (fallbacks when site details missing)
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"address":"seeded address","mode":"satellite-only"}'

# Photo mode (image-based assessment)
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"address":"Photo site","mode":"photo"}'
```

**Expected response** (200): `assessment_id`, `pdf_url`, `confidence`, `scenarios`.

**UI**: Intake → Step 1 → "Assessment → Input mode" (Address | Satellite only | Photo).

---

## 3. Bulk Upload Demo

### Upload Sample CSV
```bash
curl -X POST http://localhost:8000/api/bulk/upload \
  -F "file=@data/sample_bulk.csv"
```

**Expected Response**:
```json
{"job_id": "abc123-...", "status": "processing", "rows_total": 100}
```

### Check Job Status
```bash
curl http://localhost:8000/api/bulk/status/{job_id}
```

**Expected Result**:
- `rows_processed`: ~100
- `rows_success`: ~85+
- `rows_failed`: ~15 (expected edge cases)

### Download Results
```bash
curl -O http://localhost:8000/api/bulk/{job_id}/download.zip
unzip download.zip  # Contains individual PDFs
```

---

## 4. Photo Verification Demo

### Via Web UI
1. Navigate to http://localhost:5173/verification
2. Upload sample verification photo (from `data/sample_images/`)
3. GPS is auto-extracted from EXIF
4. View AI confidence scores
5. See auto-verify or manual review status

### Via API
```bash
curl -X POST http://localhost:8000/api/verification \
  -F "project_id=1" \
  -F "photos=@data/sample_images/tank_photo.jpg" \
  -F "gps_lat=28.6139" \
  -F "gps_lng=77.2090"
```

**Expected Response**:
```json
{
  "verification_id": "ver_xxx",
  "status": "verified",
  "ai_confidence": {"tank_present": 0.92, "diverter_present": 0.75},
  "audit_hash": "sha256:abc..."
}
```

---

## 5. IoT Monitoring Demo

### Run Sensor Simulator
```bash
# Simulate 24 hours of data
python tools/sensor_sim.py --hours 24 --interval 300 --dry-run

# Or post to live API
python tools/sensor_sim.py --hours 24 --interval 300
```

### View Monitoring Dashboard
1. Navigate to http://localhost:5173/monitoring
2. See tank level gauge (should NOT show "NaN%")
3. View 24-hour trend chart
4. Check "Days until empty" prediction

### Via API
```bash
# Post single sensor reading
curl -X POST http://localhost:8000/api/monitoring/sensor \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "SENSOR-001",
    "project_id": 1,
    "level_percent": 65.5,
    "level_volume_l": 6550,
    "battery_pct": 95.0
  }'
```

---

## 6. Marketplace Allocation Demo

### Run Allocation
```bash
curl -X POST http://localhost:8000/api/marketplace/run-allocation \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "bulk_job_123",
    "weight_config": {
      "price": 0.4,
      "sla": 0.3,
      "distance": 0.2,
      "rating": 0.1
    }
  }'
```

**Expected Response**:
```json
{
  "allocations": [
    {
      "project_id": 1,
      "installer_id": 5,
      "score": 0.85,
      "score_breakdown": {"price": 0.32, "sla": 0.28, "distance": 0.15, "rating": 0.10}
    }
  ]
}
```

---

## 7. PDF Report Demo

### Generate Assessment Report
```bash
curl -O http://localhost:8000/api/reports/123/pdf
```

**PDF Contents**:
- Project details with map snapshot
- 3 scenario comparison table
- Monthly capture breakdown chart
- Bill of Materials
- Subsidy calculation
- Audit verification hash in footer

---

## 8. Run Acceptance Tests

```bash
# Install test dependencies
pip install pytest pytest-bdd requests

# Run all tests
cd tests
pytest --bdd

# Run specific feature
pytest --bdd features/acceptance.feature
```

**Expected Result**: All scenarios should pass (green)

---

## 9. ML Explainability Demo

### Get Explanation for ML Run
```bash
curl http://localhost:8001/explain/{run_id}
```

**Example Response**:
```json
{
  "model_version": "v1.0.0",
  "calculation_steps": [
    "Annual rainfall sum: 790.5mm",
    "Runoff coefficient (C): 0.85",
    "Annual yield: 250 × 790.5 × 0.85 = 168,000 L"
  ],
  "confidence": 0.95
}
```

---

## 10. Security Verification

### Test Authentication
```bash
# Should return 401
curl http://localhost:8000/api/project/1

# With token (should succeed)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/project/1
```

### Test Rate Limiting
```bash
# Make many requests quickly
for i in {1..100}; do curl -s http://localhost:8000/api/health; done
# Some should return 429
```

---

## Cleanup

```bash
docker-compose down -v  # Stops services and removes volumes
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "NaN%" in tank level | Fixed in latest version - refresh page |
| Container fails to start | Check logs: `docker-compose logs backend` |
| Database not initialized | Run: `docker-compose exec db psql -U user -d rainforge -f /docker-entrypoint-initdb.d/init.sql` |
| Frontend build error | Clear cache: `cd frontend && rm -rf node_modules && npm install` |

---

## Contact

**Owners**: Prashant Mishra & Ishita Parmar  
**Project**: RainForge - Jal Shakti Hackathon 2026
