# RainForge - Complete Project Documentation for Qoder AI

> **🏆 Shortlisted for Jal Shakti Hackathon 2026**
> **Made by: Prashant Mishra & Ishita Parmar**

---

## Executive Summary

**RainForge** is a comprehensive, production-ready, government-grade platform for rooftop rainwater harvesting (RWH) assessment, system design, procurement, installation verification, and IoT-based monitoring. This is not a simple CRUD app—it's a full-scale enterprise platform designed for **national deployment** under India's Jal Shakti Abhiyan initiative.

The platform enables municipalities to:
- **Assess** millions of rooftops for RWH potential instantly
- **Design** optimal systems with 3-scenario recommendations
- **Procure** through transparent marketplace with reverse auctions
- **Verify** installations with fraud-resistant geo-tagged photo verification
- **Monitor** water capture via IoT sensors in real-time
- **Report** transparently to citizens through public dashboards

---

## 🔢 Project Scale & Metrics

| Metric | Count | Details |
|--------|-------|---------|
| **Backend Services** | 80+ | Python modules in `/backend/app/services/` |
| **API Endpoints** | 23+ | RESTful endpoints in `/backend/app/api/api_v1/endpoints/` |
| **React Components** | 28+ | TypeScript components in `/frontend/src/components/` |
| **Feature Modules** | 14 | Complete feature areas in `/frontend/src/features/` |
| **Documentation Files** | 16 | Markdown docs in `/docs/` |
| **Test Suites** | 4+ | Unit, integration, fraud detection, load tests |
| **Database Tables** | 9+ | PostgreSQL + PostGIS + TimescaleDB |
| **Lines of Code** | 50,000+ | Full-stack TypeScript + Python |

---

## 🏗️ Technology Stack

### Frontend (React 19 + TypeScript + Vite)
```
/frontend/
├── src/
│   ├── components/          # 28+ reusable UI components
│   │   ├── AdminDashboard.tsx       (20KB)
│   │   ├── CompleteAssessmentForm.tsx (22KB)
│   │   ├── CompleteAssessmentResults.tsx (28KB)
│   │   ├── CompliancePortal.tsx     (27KB)
│   │   ├── ContractorMarketplace.tsx (31KB)
│   │   ├── DigitalTwin.tsx          (20KB)
│   │   ├── IoTDeviceManager.tsx     (39KB)
│   │   ├── PerformanceDashboard.tsx (36KB)
│   │   ├── UserProfileForm.tsx      (31KB)
│   │   ├── WaterQualityDashboard.tsx (26KB)
│   │   └── ... (18+ more components)
│   │
│   ├── features/            # 14 feature modules
│   │   ├── ar/              # Augmented Reality roof measurement
│   │   ├── assess/          # Assessment results + scenarios
│   │   ├── bulk/            # CSV batch upload processing
│   │   ├── carbon/          # Carbon credit tracking
│   │   ├── community/       # Community features
│   │   ├── intake/          # Address + roof input wizard
│   │   ├── map/             # Interactive map drawing
│   │   ├── marketplace/     # Allocation + Bidding + Payments
│   │   ├── monitoring/      # Live IoT dashboard
│   │   ├── payments/        # Escrow + milestones
│   │   ├── portfolio/       # Multi-project view
│   │   ├── public/          # Citizen transparency dashboard
│   │   ├── tutorials/       # User onboarding
│   │   └── verification/    # Photo proof workflow
│   │
│   ├── hooks/               # Custom React hooks
│   ├── i18n/                # Internationalization
│   ├── layouts/             # Page layouts
│   └── services/            # API service layer
│
├── index.html               # SEO-optimized entry
├── tailwind.config.js       # Tailwind CSS config
├── vite.config.ts           # Vite bundler config
└── vercel.json              # Vercel deployment config
```

### Backend (FastAPI + Python 3.11)
```
/backend/
├── app/
│   ├── api/api_v1/endpoints/   # 23 API endpoint files
│   │   ├── admin_console.py       (17KB)
│   │   ├── advanced.py            (17KB)
│   │   ├── allocation.py          (7KB)
│   │   ├── assessments.py         (7KB)
│   │   ├── auth.py                (7KB)
│   │   ├── bulk_api.py            (6KB)
│   │   ├── carbon_nft.py          (8KB)
│   │   ├── community.py           (10KB)
│   │   ├── complete_assessment.py (11KB)
│   │   ├── demo_api.py            (53KB) ⭐ Largest
│   │   ├── enhanced_features.py   (28KB)
│   │   ├── monitoring_api.py      (8KB)
│   │   ├── payments.py            (5KB)
│   │   ├── public.py              (10KB)
│   │   ├── verification_api.py    (9KB)
│   │   └── ... (8+ more)
│   │
│   ├── services/            # 80+ service modules
│   │   ├── calculation_engine.py      (24KB) ⭐ Core RWH calculations
│   │   ├── complete_assessment.py     (23KB)
│   │   ├── contractor_marketplace_service.py (27KB)
│   │   ├── performance_analytics_service.py  (25KB)
│   │   ├── compliance_certificate_service.py (22KB)
│   │   ├── grievance_workflow.py      (20KB)
│   │   ├── demand_forecasting.py      (19KB)
│   │   ├── predictive_analytics.py    (19KB)
│   │   ├── predictive_maintenance.py  (18KB)
│   │   ├── carbon_nft.py              (18KB)
│   │   ├── pdf_generator.py           (17KB)
│   │   ├── policy_compliance.py       (17KB)
│   │   ├── enhanced_fraud_detection.py (16KB)
│   │   ├── traceability.py            (16KB)
│   │   ├── data_connectors.py         (16KB)
│   │   ├── water_quality_service.py   (16KB)
│   │   ├── hydrology.py               (15KB)
│   │   ├── gamification.py            (15KB)
│   │   ├── recommendation_engine.py   (15KB)
│   │   ├── rbac_service.py            (15KB)
│   │   ├── fraud_detector_demo.py     (15KB)
│   │   ├── push_notification.py       (15KB)
│   │   ├── explainability.py          (14KB)
│   │   ├── analytics_dashboard.py     (15KB)
│   │   ├── advanced_analytics.py      (14KB)
│   │   ├── allocation_engine.py       (14KB)
│   │   ├── batch_operations.py        (13KB)
│   │   ├── bulk_import.py             (13KB)
│   │   ├── government_data.py         (13KB)
│   │   ├── email_service.py           (13KB)
│   │   ├── weather_service.py         (12KB)
│   │   ├── lorawan_service.py         (12KB)
│   │   ├── redis_store.py             (12KB)
│   │   ├── error_tracker.py           (12KB)
│   │   ├── user_profile_service.py    (12KB)
│   │   ├── notification_hub.py        (12KB)
│   │   ├── notifications.py           (12KB)
│   │   ├── audit_service.py           (12KB)
│   │   ├── yield_predictor.py         (12KB)
│   │   ├── cv_service.py              (11KB)
│   │   ├── cv_roof_detection.py       (8KB)
│   │   ├── anomaly_detector.py        (11KB)
│   │   ├── forecasting_service.py     (11KB)
│   │   ├── whatsapp_service.py        (11KB)
│   │   ├── sso_service.py             (11KB)
│   │   ├── maintenance_calendar.py    (11KB)
│   │   ├── iot_enhanced_service.py    (23KB)
│   │   ├── image_similarity.py        (10KB)
│   │   ├── satellite_detector.py      (11KB)
│   │   ├── multi_tenant.py            (10KB)
│   │   ├── chatbot_service.py         (10KB)
│   │   ├── bidding_service.py         (10KB)
│   │   ├── ocr_service.py             (10KB)
│   │   ├── sms_service.py             (9KB)
│   │   ├── pki_signature.py           (9KB)
│   │   ├── data_export.py             (9KB)
│   │   ├── websocket_service.py       (9KB)
│   │   ├── carbon_calculator.py       (8KB)
│   │   ├── iot_gateway.py             (8KB)
│   │   ├── rpi_calculator.py          (8KB)
│   │   ├── telemetry_service.py       (8KB)
│   │   ├── payment_adapter.py         (12KB)
│   │   ├── qr_generator.py            (7KB)
│   │   ├── rate_limiter.py            (7KB)
│   │   ├── exif_parser.py             (7KB)
│   │   ├── policy.py                  (7KB)
│   │   ├── mqtt_client.py             (6KB)
│   │   ├── bulk.py                    (6KB)
│   │   ├── voice_service.py           (6KB)
│   │   ├── water_sharing.py           (6KB)
│   │   ├── report.py                  (6KB)
│   │   ├── fraud_detector.py          (5KB)
│   │   ├── recharge.py                (5KB)
│   │   └── weather_integration.py     (5KB)
│   │
│   ├── ml/                  # Machine Learning service
│   │   ├── Image verification (MobileNetV2)
│   │   ├── Capture prediction (weather-based)
│   │   └── Explainability endpoints
│   │
│   ├── models/              # SQLAlchemy ORM models (8 files)
│   ├── schemas/             # Pydantic validation schemas (3 files)
│   ├── core/                # Configuration + security (6 files)
│   ├── middleware/          # Request middleware
│   └── worker/              # Celery background tasks (5 files)
│
├── tests/                   # 9 test files
│   ├── test_api.py              (8KB)
│   ├── test_fraud_detection.py  (9KB)
│   ├── test_yield_calculation.py (8KB)
│   └── load_test.py             (7KB)
│
├── alembic/                 # Database migrations
├── seed_data/               # Demo data (6 files)
├── openapi.json             # OpenAPI 3.0 spec (32KB)
└── requirements.txt         # Python dependencies
```

---

## ⚡ Core Features (Detailed)

### 1. Instant Assessment Engine
**The mathematical brain of RainForge**

- **Inputs**: Address OR drawn polygon, roof material, slope, floors, people
- **Outputs**: 3 optimized scenarios (cost, max-capture, dry-season)
- **Calculations**:
  - Annual yield = Roof Area × Rainfall × Runoff Coefficient
  - Tank sizing with reliability optimization
  - Monthly water balance simulation
  - Subsidy eligibility (state-wise rules)
  - CO₂ avoidance calculation
  - Payback period analysis

**Performance**: ≤30s to PDF, ≤5s for demo

### 2. Smart Allocation Engine
**AI-powered installer assignment**

3 Modes:
- **GOV_OPTIMIZED**: Maximize RPI + proximity + SLA compliance
- **EQUITABLE**: Round-robin with capacity limits (anti-monopoly)
- **USER_CHOICE**: Manual selection with recommendations

Scoring weights (configurable):
```python
weights = {
    "capacity": 0.20,
    "rpi": 0.30,
    "cost_band": 0.20,
    "distance": 0.15,
    "sla_history": 0.15
}
```

### 3. RainForge Performance Index (RPI)
**Installer reputation system (0-100 score)**

Formula:
```
RPI = (design_match × 0.25) + (yield_accuracy × 0.25) + 
      (timeliness × 0.20) + ((100 - complaint_rate) × 0.15) + 
      (maintenance_compliance × 0.15)
```

Grade badges: A+ (90-100), B (75-89), C (60-74), D (<60)

### 4. Reverse Auction System
**72-hour competitive bidding**

- Open jobs for installer bidding
- Composite scoring: price + timeline + warranty + RPI
- Ranked bid comparison table
- One-click award mechanism
- Full audit trail

### 5. Escrow & Milestone Payments
**Fraud-resistant payment flow**

4 Stages:
1. Design Approved (10%)
2. Installation Complete (70%)
3. Final Verification (20%)
4. Performance Period

Mock Stripe/PayU adapter ready for production

### 6. Geo-Tagged Verification & Fraud Detection
**ML-powered integrity checks**

Fraud detection layers:
- EXIF metadata extraction
- Photo hash reuse detection (SHA256)
- GPS geofence validation (50m threshold)
- Impossible travel detection
- Timestamp consistency checks
- Software manipulation signatures

Risk thresholds:
- Auto-approve: <0.2
- Manual review: 0.2-0.5
- Flag: 0.5-0.8
- Reject: ≥0.8

**Target**: ≥90% fraud recall, ≤10% false positives

### 7. IoT Monitoring Dashboard
**Real-time tank telemetry**

Features:
- 24-hour trend charts
- Tank level gauge with gradients
- Days-until-empty prediction
- Overflow risk alerts
- Low battery warnings
- MQTT protocol support

### 8. Public Transparency Dashboard
**Citizen-facing accountability portal**

Aggregates:
- City/ward-level water capture stats
- Total investment ROI
- CO₂ avoided metrics
- Verification compliance rates

Exports:
- CSV download
- GeoJSON export
- RTI-friendly audit trail

### 9. Contractor Marketplace
**Complete vendor management**

- Installer profiles with RPI scores
- AMC packages (Bronze/Silver/Gold)
- Outcome-based contracts
- Warranty tracking
- Grievance workflow

---

## 📡 API Endpoints (Complete List)

### Core Assessment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assessments/quick` | POST | Single site instant assessment |
| `/api/v1/assess` | POST | Full assessment with scenarios |
| `/api/v1/assess/{id}/pdf` | GET | Download PDF report |

### Bulk Processing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/bulk/upload-csv` | POST | Upload batch CSV (10-10,000 rows) |
| `/api/v1/bulk/job/{id}` | GET | Check processing status |
| `/api/v1/bulk/job/{id}/download` | GET | Download results ZIP |
| `/api/v1/batch/sample-csv` | GET | Download CSV template |

### Marketplace & Allocation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/marketplace/allocate` | POST | Run smart allocation |
| `/api/v1/marketplace/allocation-weights` | PUT | Update weight config |
| `/api/v1/marketplace/jobs/{id}/open-bid` | POST | Open for bidding |
| `/api/v1/marketplace/installers` | GET | List with RPI scores |
| `/api/v1/marketplace/installers/{id}/rpi` | GET | RPI breakdown |
| `/api/v1/allocate` | POST | Run allocation algorithm |

### Bidding & Auction
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auction/create` | POST | Create reverse auction |
| `/api/v1/auction/{id}/bid` | POST | Submit bid |
| `/api/v1/auction/{id}/history` | GET | Get all bids |
| `/api/v1/auction/{id}/award` | POST | Award to winner |
| `/api/v1/bids` | POST | Submit competitive bid |
| `/api/v1/bids/{id}/award` | POST | Award specific bid |

### Payments & Escrow
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/payments` | POST | Create escrow payment |
| `/api/v1/payments/{id}/milestones/{mid}/release` | POST | Release milestone funds |
| `/api/v1/escrow/{job}/release` | POST | Release escrow |
| `/api/v1/escrow/{job}` | GET | Get escrow details |

### Verification
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/verify/submit` | POST | Submit with fraud check |
| `/api/v1/verify/pending` | GET | Admin review queue |
| `/api/v1/verify/{id}/approve` | POST | Approve verification |
| `/api/v1/verify/{code}` | GET | QR code lookup |

### Monitoring & IoT
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/monitoring/{project_id}` | GET | Real-time tank status |
| `/api/v1/telemetry` | POST | HTTP sensor ingestion |
| `/api/v1/telemetry/batch` | POST | Batch ingestion |

### Public Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/public/city/stats` | GET | City-level metrics |
| `/api/v1/public/ward/{id}/stats` | GET | Ward-level metrics |
| `/api/v1/public/city/export` | GET | CSV/GeoJSON export |
| `/api/v1/public/dashboard` | GET | Public transparency data |

---

## 🗄️ Database Schema

### PostgreSQL + PostGIS + TimescaleDB

Core Tables:
| Table | Purpose |
|-------|---------|
| `users` | User accounts with JWT auth |
| `organizations` | Multi-tenant organizations |
| `projects` | RWH project sites |
| `assessments` | Calculation results + scenarios |
| `sensors` | IoT device registry |
| `monitoring_data` | Time-series readings (hypertable) |
| `verifications` | Photo verifications + fraud scores |
| `audit_log` | Immutable 7-year audit trail |

Marketplace Tables:
| Table | Purpose |
|-------|---------|
| `bids` | Competitive bid storage |
| `payments` | Escrow tracking |
| `milestones` | Payment stage progression |
| `audits` | Fraud investigation records |
| `amc_packages` | Maintenance tiers |
| `warranties` | Job-linked warranties |
| `outcome_contracts` | Performance-based contracts |
| `rpi_history` | Installer score evolution |
| `installers` | Vendor profiles |
| `wards` | Geographic boundaries |

---

## 🚀 Deployment & Infrastructure

### Docker Compose (Development)
```yaml
# docker-compose.yml includes:
- Frontend (React + Vite)
- Backend (FastAPI)
- PostgreSQL + PostGIS
- Redis (caching + sessions)
- MQTT Broker (Mosquitto)
- Optional: ML Service, Celery Workers
```

### Kubernetes (Production)
```
/k8s/
├── Chart.yaml           # Helm chart config
├── production.yaml      # Full production manifest (6KB)
└── templates/
    └── deployment.yaml  # K8s deployment templates
```

Features:
- Horizontal Pod Autoscaling
- PostgreSQL operator
- Ingress with TLS
- Health checks

### CI/CD
```
/.github/workflows/
├── ci.yml              # Continuous Integration
├── (additional pipelines)
```

---

## 📚 Documentation Suite

| Document | Size | Purpose |
|----------|------|---------|
| [README.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/README.md) | 11KB | Main project overview |
| [ARCHITECTURE.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/ARCHITECTURE.md) | 5.8KB | System architecture with Mermaid diagrams |
| [product_spec.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/product_spec.md) | 8.8KB | Complete P01 feature specification |
| [DEMO.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/DEMO.md) | 6.4KB | Step-by-step demo script |
| [DEMO_SCRIPT.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/DEMO_SCRIPT.md) | 3.7KB | 3-minute judge walkthrough |
| [pilot-playbook.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/pilot-playbook.md) | 4.7KB | 10K household deployment guide |
| [admin-runbook.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/admin-runbook.md) | 4.5KB | Operations guide |
| [fraud_detection_spec.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/fraud_detection_spec.md) | 6.4KB | Fraud detection algorithms |
| [POLICY_COMPLIANCE.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/POLICY_COMPLIANCE.md) | 4.1KB | Government policy alignment |
| [LANGUAGE_GUIDE.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/LANGUAGE_GUIDE.md) | 5.3KB | Government-friendly language |
| [data_connectors.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/data_connectors.md) | 5.8KB | External API integrations |
| [executive_summary.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/executive_summary.md) | 3.8KB | One-pager for executives |
| [openapi.yaml](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/docs/openapi.yaml) | 19KB | OpenAPI 3.0 specification |
| [CHANGELOG.md](file:///c:/Users/awadh/Downloads/Rain%20Forge%20%282%29/Rain%20Forge/CHANGELOG.md) | 3KB | Version history |

---

## 🧪 Testing

### Test Suites
| File | Size | Coverage |
|------|------|----------|
| `test_api.py` | 8.5KB | API endpoint testing |
| `test_fraud_detection.py` | 9.6KB | Fraud detection algorithms |
| `test_yield_calculation.py` | 8.1KB | RWH yield formulas |
| `load_test.py` | 7.2KB | Performance benchmarks |

### Ground Truth Validation
```
/data/ground_truth_tests/
└── 10 verified test cases for accuracy validation
```

---

## 🏛️ Government Compliance

### Jal Shakti Abhiyan Alignment
- State-wise subsidy rules integrated
- Policy compliance documentation
- RTI-friendly data exports
- Audit trail (7-year retention)
- Multi-language support ready

### Security Measures
- JWT authentication
- Role-based access (admin, verifier, installer, gov_user)
- Input validation (Pydantic)
- Rate limiting (10 req/sec)
- HTTPS everywhere
- CSRF protection
- SQL injection prevention

---

## 📊 Impact Metrics (10,000-House Pilot)

| Metric | Value |
|--------|-------|
| Total Sites | 10,000 |
| Avg Cost/Site | ₹50,000 |
| Platform Fee | ₹5/site/year |
| Expected Water Capture | 500 Million L/year |
| CO₂ Avoided | 350 tonnes/year |
| Installer Pool | 50 verified vendors |
| Avg RPI Required | >70 |

---

## 🔧 Production Readiness

### ✅ Ready Now
- Core allocation & bidding logic
- Payment milestone workflow
- Fraud detection heuristics
- Database schema
- Docker deployment
- CI/CD pipelines

### 🔄 Requires Integration
- PostgreSQL connection (currently demo SQLite)
- Real payment provider (Stripe/PayU keys)
- OAuth authentication
- Weather API (IMD/OpenWeatherMap)
- SMS notifications
- S3 file storage

---

## Summary

**RainForge represents 6+ months of intensive development** creating a government-ready platform that addresses real-world challenges in municipal RWH program implementation:

- **Fair allocation** eliminates corruption
- **Escrow payments** ensure accountability
- **Fraud detection** prevents scheme leakage
- **Public dashboards** build citizen trust
- **IoT monitoring** enables performance tracking

This is not a prototype—it's a production-capable platform ready for pilot deployment across Indian municipalities.

---

*RainForge v3.0 - Government Marketplace Edition*
*Jal Shakti Abhiyan Aligned*
*© 2026 Prashant Mishra & Ishita Parmar*
