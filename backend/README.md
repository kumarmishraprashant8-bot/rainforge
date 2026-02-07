# RainForge Demo - Complete Backend

🌧️ **RainForge** - End-to-end Rooftop Rainwater Harvesting Platform

## Quick Start (Demo)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the demo server
python -m uvicorn app.main_demo:app --reload --port 8000

# 5. Open API docs
# http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assess` | POST | Create RWH assessment (3 scenarios) |
| `/api/v1/assess/{id}/pdf` | GET | Download PDF with QR + signature |
| `/api/v1/auction/create` | POST | Create reverse auction |
| `/api/v1/auction/{id}/bid` | POST | Submit bid |
| `/api/v1/allocate` | POST | Allocate installers to jobs |
| `/api/v1/escrow/{job}/release` | POST | Release milestone payment |
| `/api/v1/verify` | POST | Submit verification photos |
| `/api/v1/verify/{code}` | GET | Verify assessment via QR |
| `/api/v1/monitoring/{id}` | GET | Get IoT telemetry |
| `/api/v1/installers` | GET | List installers with RPI |
| `/api/v1/public/dashboard` | GET | Public transparency data |

## Demo Walkthrough (2 Minutes)

### 0:00-0:30 - Assessment
```bash
curl -X POST http://localhost:8000/api/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "DEMO-001",
    "address": "Civic Centre, Sector 17, Chandigarh",
    "lat": 30.7333,
    "lng": 76.7794,
    "roof_area_sqm": 500,
    "roof_material": "concrete",
    "demand_l_per_day": 2000,
    "state": "Punjab",
    "city": "Chandigarh"
  }'
```

**Expected output:**
- 3 scenarios: `cost_optimized`, `max_capture`, `dry_season`
- PDF URL with QR verification
- Subsidy calculation

### 0:30-1:00 - Allocation
```bash
# List installers with RPI scores
curl http://localhost:8000/api/v1/installers

# Allocate using government-optimized mode
curl -X POST http://localhost:8000/api/v1/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "job_ids": ["JOB-XXXXX"],
    "mode": "gov_optimized"
  }'
```

### 1:00-1:30 - Auction
```bash
# Create auction
curl -X POST http://localhost:8000/api/v1/auction/create \
  -H "Content-Type: application/json" \
  -d '{"job_id": "JOB-XXXXX", "deadline_hours": 72}'

# Submit bid
curl -X POST http://localhost:8000/api/v1/auction/AUC-XXXXX/bid \
  -H "Content-Type: application/json" \
  -d '{
    "installer_id": 1,
    "price_inr": 125000,
    "timeline_days": 14,
    "warranty_months": 24
  }'
```

### 1:30-2:00 - Verification & Monitoring
```bash
# Download PDF (open in browser)
http://localhost:8000/api/v1/assess/ASM-XXXXX/pdf

# Verify via QR code
curl http://localhost:8000/api/v1/verify/{qr_code}

# Check IoT monitoring
curl http://localhost:8000/api/v1/monitoring/1?hours=24
```

## Database

### Demo Mode (Default)
Uses SQLite - no configuration needed:
```
sqlite:///./rainforge_demo.db
```

### Production Mode
Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/rainforge"
```

## Seed Data

Demo automatically seeds:
- 6 installers with varied RPI scores (45-92)
- 10 state subsidy rules (Delhi, Maharashtra, Karnataka, etc.)
- Sample assessments
- 72 hours of telemetry data
- 3 ward boundaries

### Files
```
seed_data/
├── seed_installers.csv
├── subsidy_rules.csv
├── seed_telemetry.json
└── sample_wards.geojson
```

## Fraud Detection

Verification photos are analyzed for:

| Check | Score | Description |
|-------|-------|-------------|
| No EXIF | +0.4 | Missing metadata |
| No GPS | +0.3 | No location in photo |
| Location severe | +0.6 | >500m from site |
| Location moderate | +0.3 | 200-500m from site |
| Photo reuse | +0.8 | Duplicate hash detected |
| Software edited | +0.5 | Photoshop/GIMP detected |
| Timestamp old | +0.2 | Photo >48 hours old |
| Travel anomaly | +0.4 | Impossible travel speed |

**Recommendations:**
- Score < 0.2: `auto_approve`
- Score 0.2-0.5: `review`
- Score 0.5-0.8: `manual_review`
- Score > 0.8: `reject`

## RPI Calculation

RainForge Performance Index (0-100):

| Component | Weight | Description |
|-----------|--------|-------------|
| Timeliness | 25% | SLA compliance % |
| Capacity | 15% | Available slots |
| Cost | 20% | Price competitiveness |
| Experience | 20% | Jobs completed |
| Certification | 10% | basic/certified/premium |
| Warranty | 10% | Months offered |

## External Data Sources

### Rainfall (Swap Connectors)

**Primary: Open-Meteo (Free)**
```python
# Already integrated
# No API key required
```

**Fallback: IMD**
```python
# Placeholder - requires registration
# See: https://imd.gov.in/api
```

**Historical: CHIRPS**
```bash
# Download NetCDF from:
# https://data.chc.ucsb.edu/products/CHIRPS-2.0/
# Place in data/chirps/
```

### Geocoding: Nominatim
```python
# Rate limited: 1 request/second
requests.get("https://nominatim.openstreetmap.org/search", 
             params={"q": "address", "format": "json"})
```

### Groundwater: CGWB
```
# Source CSV from:
# http://cgwb.gov.in/data.html
# Place in data/cgwb/
```

### Subsidy Rules
```
# State portals:
# - Delhi: https://delhijalboard.nic.in
# - Maharashtra: https://mahawater.gov.in
# - Karnataka: https://bwssb.gov.in
# Update seed_data/subsidy_rules.csv
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Test specific module
pytest tests/test_demo_api.py -v -k "assessment"
```

## Project Structure

```
backend/
├── app/
│   ├── api/api_v1/endpoints/
│   │   ├── demo_api.py        # All demo endpoints
│   │   └── complete_assessment.py
│   ├── models/
│   │   └── database.py        # SQLAlchemy models
│   ├── services/
│   │   ├── pdf_generator_demo.py
│   │   ├── fraud_detector_demo.py
│   │   └── exif_parser.py
│   ├── main_demo.py           # FastAPI app
│   └── seed_data.py           # Demo data seeding
├── tests/
│   └── test_demo_api.py
├── seed_data/                  # CSV/JSON seed files
├── uploads/                    # Verification photos
├── generated_pdfs/             # Generated PDFs
├── requirements.txt
├── config.example.yml
├── openapi.json
└── README.md
```

## Frontend Wiring Examples

### React/TypeScript
```typescript
// Assessment
const createAssessment = async (data: AssessmentInput) => {
  const response = await fetch('/api/v1/assess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
};

// Verification
const submitVerification = async (jobId: string, lat: number, lng: number, photos: File[]) => {
  const formData = new FormData();
  formData.append('job_id', jobId);
  formData.append('lat', lat.toString());
  formData.append('lng', lng.toString());
  photos.forEach(photo => formData.append('photos', photo));
  
  const response = await fetch('/api/v1/verify', {
    method: 'POST',
    body: formData
  });
  return response.json();
};
```

### Fetch in existing components
```typescript
// ContractorMarketplace.tsx
useEffect(() => {
  fetch('/api/v1/installers?min_rpi=60')
    .then(res => res.json())
    .then(data => setInstallers(data.installers));
}, []);

// IoTMonitoring.tsx
useEffect(() => {
  fetch(`/api/v1/monitoring/${projectId}?hours=24`)
    .then(res => res.json())
    .then(data => setTelemetry(data));
}, [projectId]);
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./rainforge_demo.db` | Database connection |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | SQL echo logging |
| `ENVIRONMENT` | `demo` | demo/staging/production |

## License

Built for BHARAT WIN P01 Hackathon - Jal Shakti Ministry

---

**🌧️ Every Drop Counts - RainForge**
