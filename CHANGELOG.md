# Changelog

All notable changes to RainForge will be documented in this file.

## [Unreleased]

### Added (Grand success features – engagement, shareability, trust)
- **Water Security Index (0–100)**: Single score per assessment (yield, coverage, ROI, subsidy, recharge). Returned in multimodal assessment and via `GET /api/v1/success/impact`.
- **Water credits**: Impact currency (1 credit per 1000 L potential). Shown on assessment result and in Impact card.
- **Ward leaderboard**: `GET /api/v1/success/leaderboard` – top wards by systems and water captured. Displayed on Public Dashboard.
- **Crisis / alert mode**: `GET /api/v1/success/crisis` and `POST /api/v1/success/crisis` for water-alert banner. Global dismissible banner in app layout.
- **Badges (gamification)**: First Drop, Water Saver, Water Champion, High Security. Returned with assessment and in `GET /api/v1/success/badges`.
- **Impact card + Share**: On assessment results – Water Security Index, credits, equivalent showers, badges, and “Share my impact” (Web Share API or copy).
- **Success API router**: `app/api/api_v1/endpoints/success.py` and `app/services/success_features.py`; mounted in main and demo app.

### Added (Feature A - Instant multi-modal assessment)
- **Multi-modal assessment**: Optional `mode` on assessment creation: `address` | `satellite-only` | `photo`. Same 1-page engineer PDF and a `confidence` score in JSON.
- **Backend**: `POST /api/v1/assessments` (JSON body) with optional `mode`; pipeline selector in `app/services/assessment_pipeline.py`; existing `POST /api/v1/assessments/assess` unchanged.
- **Frontend**: "Assessment → Input mode" selector on Intake (Step 1): Address | Satellite only | Photo; PDF download uses `pdf_url` when present.
- **Tests**: Unit tests for pipeline selector and confidence; integration tests for each mode and PDF download.

## [1.0.0] - 2026-02-03

### Added

#### Backend API Endpoints
- `POST /api/v1/assess` - Single-site assessment with 3 scenarios
- `POST /api/v1/batch/assess` - Batch CSV processing (10-10,000 rows)
- `GET /api/v1/batch/sample-csv` - Sample CSV template download
- `POST /api/v1/auction/create` - Create reverse auction for job
- `POST /api/v1/auction/{id}/bid` - Submit bid with price/timeline/warranty
- `GET /api/v1/auction/{id}/history` - Get all bids for auction
- `POST /api/v1/auction/{id}/award` - Award auction to winning bid
- `POST /api/v1/allocate` - Smart allocation (gov_optimized, equitable, user_choice)
- `POST /api/v1/escrow/{job_id}/release` - Release milestone payment
- `GET /api/v1/escrow/{job_id}` - Get escrow details
- `POST /api/v1/verify` - Submit verification with photos
- `GET /api/v1/verify/{code}` - QR code verification lookup
- `GET /api/v1/monitoring/{project_id}` - Real-time tank monitoring
- `POST /api/v1/telemetry` - HTTP telemetry ingestion
- `POST /api/v1/telemetry/batch` - Batch telemetry ingestion
- `GET /api/v1/public/dashboard` - Public transparency dashboard
- `GET /api/v1/public/export` - CSV/GeoJSON export
- `GET /api/v1/installers` - List installers with RPI scores
- `GET /api/v1/installers/{id}/rpi` - Detailed RPI breakdown

#### Database
- PostgreSQL + PostGIS schema via Alembic migrations
- Tables: assessments, jobs, auctions, bids, verifications, escrows, telemetry, installers, wards
- Performance indexes for common queries
- Seed data for demo (6 installers, 50 sites, ward boundaries)

#### Fraud Detection
- SHA256 photo hash duplicate detection
- Haversine distance geo-mismatch detection (>150m = high risk)
- EXIF GPS extraction and validation
- Risk score calculation (0-100) with reason array
- Auto-approve / manual-review / fraud-flag workflow

#### PDF Generation
- Assessment PDF with QR code for verification
- Engineer digital signature block
- Component cost breakdown
- Three scenario comparison

#### Infrastructure
- Docker Compose with PostgreSQL, MQTT (Mosquitto), Redis
- GitHub Actions CI pipeline
- Automated demo playback script

#### Documentation
- OpenAPI 3.0 specification (769 lines)
- Demo walkthrough guide
- API testing examples

### Fixed
- Frontend mock data replaced with instant responses for demo speed
- Monitoring chart rendering with proper gradient colors
- Tank level gauge with vibrant gradient styling

---

## Acceptance Criteria Checklist

- [x] All unit + integration tests pass
- [x] `POST /batch/assess` processes CSV and returns results
- [x] `GET /assess/{id}/pdf` returns PDF with embedded QR
- [x] `POST /verify` computes risk_score and detects duplicate photos
- [x] Auction flow test: create → bid → allocate → award
- [x] Alembic migrations apply cleanly
- [x] Frontend marketplace interactions succeed in demo mode
