# RainForge Product Specification (P01 Compliance)

## Executive Summary

RainForge is a complete end-to-end platform for rooftop rainwater harvesting assessment, system design, procurement, installation, verification, and monitoring. This specification details all features required for BHARAT WIN P01 hackathon compliance.

---

## Problem Statement (P01)

Build an instant on-the-spot rooftop RWH assessment + system design tool that:
- Provides instant assessment from address/location
- Generates engineer-signed PDF reports
- Supports batch processing for government scale
- Includes fraud-resistant verification
- Enables IoT-based monitoring

---

## Feature Matrix

| Feature | Status | Priority | Acceptance Criteria |
|---------|--------|----------|---------------------|
| Instant Assessment | ✅ Complete | P0 | ≤30s to PDF |
| Batch CSV Processing | ✅ Complete | P0 | 1000 rows/min |
| PDF Generation | ✅ Complete | P0 | QR + engineer signature |
| RPI Scoring | ✅ Complete | P0 | Documented formula |
| Smart Allocation | ✅ Complete | P0 | 3 modes working |
| Reverse Auction | ✅ Complete | P1 | 72-hour bidding |
| Escrow Milestones | ✅ Complete | P1 | 3-stage release |
| Fraud Detection | ✅ Complete | P0 | ≥90% recall |
| IoT Telemetry | ✅ Complete | P1 | 24h charts |
| Public Dashboard | ✅ Complete | P1 | Ward aggregates |

---

## Feature Specifications

### 1. Instant Assessment Engine

**Spec**: Given address OR drawn roof polygon, compute RWH system design.

**Inputs**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| address | string | Yes* | Geocodable |
| polygon | GeoJSON | Yes* | Valid polygon |
| roof_material | enum | Yes | concrete, metal, tiles |
| slope_degrees | float | No | 0-45° |
| floors | int | Yes | 1-20 |
| people | int | Yes | 1-500 |
| monthly_bill_inr | float | No | 0-100000 |

*Either address or polygon required

**Outputs**:
```json
{
  "assessment_id": "ASM-20260203-001",
  "roof_area_sqm": 150,
  "annual_yield_liters": 89250,
  "scenarios": {
    "cost_optimized": {"tank_l": 3000, "cost_inr": 28000},
    "max_capture": {"tank_l": 8000, "cost_inr": 52000},
    "dry_season": {"tank_l": 5000, "cost_inr": 38000}
  },
  "monthly_balance": [...],
  "reliability_pct": 72.5,
  "subsidy": {"pct": 50, "amount_inr": 14000},
  "net_cost_inr": 14000,
  "co2_avoided_kg": 22.8,
  "payback_years": 4.2,
  "pdf_url": "/api/v1/assess/ASM-20260203-001/pdf"
}
```

**Acceptance Criteria**:
- Latency: ≤30 seconds median (≤5s demo target)
- Accuracy: ±10% vs ground truth (10 test cases)
- PDF generated with unique QR verification code

**API**: `POST /api/v1/assess`

---

### 2. Batch/Bulk Assessment

**Spec**: Process CSV of 10-10,000 sites with progress tracking.

**CSV Schema**:
```csv
site_id,address,lat,lng,roof_area_sqm,roof_material,floors,people
```

**Process Flow**:
1. Upload CSV → Validate → Create job
2. Background workers process rows
3. Generate per-row JSON + PDF
4. Create aggregate ward report
5. Package as downloadable ZIP

**Acceptance Criteria**:
- Throughput: 1,000 rows/min
- Progress: Real-time % complete
- Output: batch_results.zip with PDFs

**API**:
- `POST /api/v1/bulk/upload` → `{job_id}`
- `GET /api/v1/bulk/job/{id}` → progress
- `GET /api/v1/bulk/job/{id}/download` → ZIP

---

### 3. RainForge Performance Index (RPI)

**Spec**: Installer reliability score 0-100.

**Formula**:
```
RPI = (design_match × 0.25) + (yield_accuracy × 0.25) + 
      (timeliness × 0.20) + ((100 - complaint_rate) × 0.15) + 
      (maintenance_compliance × 0.15)
```

**Component Definitions**:
| Component | Calculation | Range |
|-----------|-------------|-------|
| design_match | % match to recommended design | 0-100 |
| yield_accuracy | actual vs predicted yield | 0-100 |
| timeliness | % jobs completed on time | 0-100 |
| complaint_rate | % jobs with complaints | 0-100 |
| maintenance_compliance | % maintenance completed | 0-100 |

**Grades**:
| Score | Grade | Badge |
|-------|-------|-------|
| 90-100 | A | ⭐ Premium |
| 75-89 | B | ✓ Certified |
| 60-74 | C | ○ Basic |
| <60 | D | ⚠ Warning |

---

### 4. Smart Allocation Engine

**Spec**: Assign installers to jobs using configurable modes.

**Modes**:
| Mode | Logic |
|------|-------|
| GOV_OPTIMIZED | Maximize RPI + proximity + SLA |
| EQUITABLE | Round-robin with capacity limits |
| USER_CHOICE | Manual selection with recommendations |

**Scoring Weights**:
```python
weights = {
    "capacity": 0.20,
    "rpi": 0.30,
    "cost_band": 0.20,
    "distance": 0.15,
    "sla_history": 0.15
}
```

**API**: `POST /api/v1/allocate`

---

### 5. Reverse Auction

**Spec**: 72-hour competitive bidding for installation jobs.

**Bid Scoring**:
```
score = (price_weight × norm_price) + 
        (quality_weight × RPI/100) + 
        (timeline_weight × norm_timeline)
```

Default weights: price=0.35, quality=0.30, timeline=0.20, warranty=0.15

**States**: `open → closed → awarded → in_progress → completed`

**API**:
- `POST /api/v1/auction/create`
- `POST /api/v1/auction/{id}/bid`
- `GET /api/v1/auction/{id}/history`

---

### 6. Escrow Milestones

**Spec**: Funds held in escrow, released per milestone.

**Default Milestones**:
| Milestone | % of Total | Release Condition |
|-----------|------------|-------------------|
| Design Approved | 10% | Admin approval |
| Installation Complete | 70% | Geo-verified photos |
| Final Verification | 20% | 30-day warranty period |

**States**: `pending → escrow → partial_released → released → refunded`

**API**: `POST /api/v1/escrow/{job}/release`

---

### 7. Geo-Tagged Verification

**Spec**: Multi-layer fraud detection for verification photos.

**Checks**:
1. EXIF metadata presence
2. GPS within geofence (50m threshold)
3. Photo hash uniqueness
4. Timestamp consistency
5. Software manipulation detection

**Thresholds**:
- auto_approve: score < 0.2
- review: score 0.2-0.5
- flag: score 0.5-0.8
- reject: score ≥ 0.8

**Acceptance Criteria**:
- Recall ≥ 90% (fraud detection)
- False positive ≤ 10%

**API**: `POST /api/v1/verify`

---

### 8. IoT Monitoring

**Spec**: Real-time tank level monitoring with alerts.

**Telemetry Payload**:
```json
{
  "device_id": "DEV-001",
  "project_id": 123,
  "timestamp": "2026-02-03T12:00:00Z",
  "readings": {
    "tank_level_liters": 3500,
    "battery_pct": 92,
    "signal_rssi": -45
  }
}
```

**Features**:
- 24-hour trend charts
- Days-until-empty prediction
- Overflow risk alerts
- Low battery warnings

**API**:
- `POST /api/v1/telemetry/ingest`
- `GET /api/v1/monitor/{project_id}`

---

### 9. Public Dashboard

**Spec**: Ward-level transparency dashboard.

**Aggregates**:
- Total water captured (liters)
- Total investment (INR)
- Average ROI
- CO₂ avoided
- % verified

**Exports**:
- CSV download
- GeoJSON export
- RTI-friendly audit trail

**API**: `GET /api/v1/public/dashboard`

---

## Demo Requirements

### Seed Data
- [x] 50 sites (mixed status)
- [x] 6 installers (varied RPI)
- [x] 24-hour telemetry
- [x] 3 ward boundaries
- [x] 10 ground truth tests

### Demo Flow (2-3 minutes)
1. Single assessment → PDF (30s)
2. Bulk upload → progress → download
3. Allocation run → installer assignment
4. Verification with fraud detection
5. Monitoring dashboard

### Deliverables
- [x] docker-compose.yml
- [x] Seed SQL script
- [x] Demo script
- [x] API documentation
- [x] 6-slide deck
- [x] Executive summary

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL + PostGIS |
| Cache | Redis |
| Queue | Celery |
| IoT | MQTT (Mosquitto) |
| Maps | Leaflet + OpenStreetMap |
| PDF | ReportLab / WeasyPrint |
| Deploy | Docker + Docker Compose |

---

## Security

- JWT authentication
- Role-based access (admin, verifier, installer, gov_user)
- Input validation (Pydantic)
- File size limits (10MB photos)
- Rate limiting
- Audit logging (7-year retention)

---

## Appendix: ROI Example

**100 m² rooftop in Delhi**:
```
Roof Area: 100 m²
Annual Rainfall: 700 mm
Runoff Coefficient: 0.85 (concrete)

Annual Capture = 100 × 0.7 × 0.85 = 59,500 L
Monthly Savings = 59,500 ÷ 12 × ₹0.05 = ₹248/month

Recommended Tank: 5,000L (₹18,000)
Installation: ₹15,000
Total: ₹33,000

Subsidy (Delhi 50%): ₹16,500
Net Cost: ₹16,500
Annual Savings: ₹2,976

Payback: 16,500 ÷ 2,976 = 5.5 years
CO₂ Avoided: 15.2 kg/year
```
