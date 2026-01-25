# RainForge Marketplace Upgrade Documentation

## Version 3.0 Upgrade Summary

This upgrade transforms RainForge from a single-site assessment tool into a **government-grade execution, procurement, and accountability platform**.

---

## New Features Added

### A. Smart Allocation Engine
**Files:** `backend/app/services/allocation_engine.py`

- 3 allocation modes: User Choice, Gov Optimized, Equitable
- Configurable weights for: Capacity, RPI, Cost Band, Distance, SLA History
- Haversine distance calculation for proximity scoring
- Admin API to update weights in real-time

### B. Competitive Bidding
**Files:** `backend/app/services/bidding_service.py`

- Open/close bidding for jobs
- Bid submission with price, timeline, warranty
- Composite scoring algorithm
- Bid ranking and award functionality

### C. RPI Calculator
**Files:** `backend/app/services/rpi_calculator.py`

- 5-component scoring: Design Match, Yield Accuracy, Timeliness, Complaint Rate, Maintenance
- Letter grades (A+ to F) with color badges
- Improvement suggestions for installers
- Historical tracking support

### D. Escrow Payments
**Files:** `backend/app/services/payment_adapter.py`

- Mock payment provider (Stripe/PayU interface)
- 4-milestone workflow: Design → Install → Verify → Performance
- Capture, verify, release fund operations
- Refund capability

### E. Fraud Detection
**Files:** `backend/app/services/fraud_detector.py`

- Photo hash reuse detection
- Geo-tag distance validation (100m threshold)
- Timestamp/travel anomaly detection
- Risk scoring with recommendations

### F. Public Dashboard
**Files:** `frontend/src/features/public/PublicDashboard.tsx`

- City and ward-level statistics
- Water capture, CO₂ avoided, beneficiaries
- CSV and GeoJSON export
- Real-time updates

---

## API Endpoints Added

### Allocation & Bidding (`/api/v1/marketplace/`)
- `POST /allocate` - Run smart allocation
- `GET /allocation-weights` - Get current weights
- `PUT /allocation-weights` - Update weights
- `POST /jobs/{id}/open-bid` - Open bidding
- `POST /bids` - Submit bid
- `GET /bids?job_id=` - List bids
- `POST /bids/{id}/award` - Award bid
- `GET /installers` - List with RPI
- `GET /installers/{id}/rpi` - RPI details

### Payments (`/api/v1/payments/`)
- `POST /` - Create payment with milestones
- `GET /{id}` - Get payment status
- `POST /{id}/escrow` - Capture to escrow
- `POST /{id}/milestones/{mid}/complete` - Complete milestone
- `POST /{id}/milestones/{mid}/verify` - Verify milestone
- `POST /{id}/milestones/{mid}/release` - Release funds

### Verification (`/api/v1/verify/`)
- `POST /submit` - Submit with fraud check
- `GET /pending` - Pending review queue
- `POST /{id}/approve` - Approve
- `POST /{id}/reject` - Reject with rework

### Public (`/api/v1/public/`)
- `GET /city/stats` - City metrics
- `GET /ward/{id}/stats` - Ward metrics
- `GET /city/export` - CSV/GeoJSON
- `GET /amc-packages` - List AMC tiers
- `POST /warranties` - Register warranty
- `POST /outcome-contracts` - Create performance contract

---

## Database Changes

### New Tables
```sql
bids              -- Competitive bidding records
payments          -- Escrow payment tracking
milestones        -- Payment stage tracking
verifications     -- Photo + geo proofs
audits            -- Fraud investigation
amc_packages      -- Maintenance packages
warranties        -- Job warranties
outcome_contracts -- Performance-based contracts
rpi_history       -- Installer score history
certifications    -- Training records
```

### Table Modifications
```sql
installers: +rpi_score, +rpi_components, +cert_level, +capacity_estimate, +is_blacklisted
jobs: +allocation_mode, +bid_status, +assigned_installer_id
```

---

## Frontend Components

| Component | Path | Purpose |
|-----------|------|---------|
| AllocationPanel | `features/marketplace/AllocationPanel.tsx` | Mode selector, weight tuning, allocation results |
| BiddingPanel | `features/marketplace/BiddingPanel.tsx` | Bid submission, ranking, award |
| PaymentMilestones | `features/payments/PaymentMilestones.tsx` | Escrow workflow UI |
| PublicDashboard | `features/public/PublicDashboard.tsx` | Citizen transparency |
| MarketplacePage | `features/marketplace/MarketplacePage.tsx` | Tab container |

---

## Migration Instructions

### 1. Database
```bash
# Create tables
psql -d rainforge -f db/migrations/001_marketplace.sql

# Seed demo data (optional)
psql -d rainforge -f db/seed_demo_data.sql
```

### 2. Backend Dependencies
No new Python dependencies required.

### 3. Frontend Dependencies
No new npm dependencies required (uses existing Recharts).

### 4. Routes
New routes added to `App.tsx`:
- `/marketplace` - Allocation, Bidding, Payments
- `/public` - Citizen dashboard
- `/public/ward/:wardId` - Ward-specific view

---

## Mocked Components (Demo Only)

| Component | Mock Behavior | Production Integration |
|-----------|--------------|------------------------|
| PaymentAdapter | In-memory escrow | Stripe/PayU API |
| FraudDetector.photo_hash | SHA256 comparison | Cloud Vision API |
| FraudDetector.geo | Haversine calculation | GPS verification service |
| PublicDashboard.stats | Static demo data | PostgreSQL aggregates |
| IoT Monitoring | Simulated readings | MQTT gateway |

---

## Testing

### Unit Tests (to add)
- `test_allocation_engine.py` - Weight scoring
- `test_rpi_calculator.py` - Component aggregation
- `test_bidding_service.py` - Bid ranking
- `test_fraud_detector.py` - Detection heuristics

### E2E Flow
1. Create job
2. Open bidding
3. Submit bids
4. Award bid
5. Create payment
6. Complete milestones
7. Submit verification
8. Approve verification
9. Release final payment

---

## Performance Notes

- Allocation engine: O(n) where n = number of installers
- Bid ranking: O(n log n) for sorting
- Fraud detection: O(1) per submission (hash lookup)
- Public dashboard: Pre-aggregated for O(1) display

---

*RainForge v3.0 Upgrade - Complete*
