# Sprint Plan - RainForge Production Readiness

**Owners**: Prashant Mishra & Ishita Parmar

---

## Week 1: Foundation & Core APIs

### Days 1-2: Infrastructure
- [x] Docker Compose with all services
- [x] Database migrations (PostgreSQL + PostGIS)
- [x] Redis, MinIO, MQTT broker setup
- [x] Nginx reverse proxy with rate limiting

### Days 3-4: Core Assessment
- [x] Calculation engine with formulas
- [x] Quick assessment API
- [x] Complete assessment (async)
- [ ] Integration with real rainfall data (IMD API)

### Days 5-7: Bulk Processing
- [x] Celery worker setup
- [x] Bulk CSV processor
- [x] Sample CSV with 100 rows
- [ ] ZIP generation with per-site PDFs

---

## Week 2: Verification & ML

### Days 1-3: Photo Verification
- [x] EXIF extraction and GPS validation
- [x] Image verification ML model (stub)
- [x] Audit log with SHA256 hashing
- [ ] AI model fine-tuning on real tank images

### Days 4-5: IoT Monitoring
- [x] Sensor data ingestion API
- [x] Sensor simulator script
- [x] Fixed NaN% bug in dashboard
- [ ] MQTT integration for real sensors

### Days 6-7: Marketplace
- [x] Installer allocation engine
- [x] Weighted scoring algorithm
- [ ] Bidding workflow UI
- [ ] Notification system

---

## Week 3: Testing & Polish

### Days 1-2: Acceptance Tests
- [x] Gherkin feature files
- [ ] pytest-bdd integration
- [ ] Load testing with locust
- [ ] Security penetration testing

### Days 3-4: UI/UX Polish
- [x] Monitoring dashboard fixes
- [ ] Admin panel for subsidies
- [ ] Hindi localization
- [ ] Mobile responsive improvements

### Days 5-7: Documentation
- [x] DEMO.md for judges
- [ ] Architecture diagrams
- [ ] API documentation (Swagger)
- [ ] Video demo recording

---

## Week 4: Production Deployment

### Days 1-2: Cloud Setup
- [ ] Kubernetes manifests
- [ ] SSL certificates
- [ ] Database backups
- [ ] Monitoring (Prometheus/Grafana)

### Days 3-4: Data Integration
- [ ] IMD rainfall data pipeline
- [ ] OpenWeatherMap forecast
- [ ] State subsidy rule updates
- [ ] Installer onboarding flow

### Days 5-7: Launch Prep
- [ ] Performance optimization
- [ ] Security audit
- [ ] User acceptance testing
- [ ] Demo rehearsal

---

## Key Deliverables Completed

| Deliverable | Status |
|-------------|--------|
| Docker Compose | ✅ Done |
| SQL Migrations | ✅ Done |
| Calculation Engine | ✅ Done |
| ML API (stub) | ✅ Done |
| Bulk Processor | ✅ Done |
| Sensor Simulator | ✅ Done |
| Sample CSV (100 rows) | ✅ Done |
| Gherkin Tests | ✅ Done |
| DEMO.md | ✅ Done |
| NaN% Bug Fix | ✅ Done |
| Nginx Config | ✅ Done |

---

## Remaining High-Priority Items

1. **Real API Integration** - Connect to IMD, OpenWeatherMap
2. **PDF Generation** - Per-site reports with BoM
3. **Load Testing** - Validate 10K row processing SLA
4. **Security Hardening** - JWT auth, API rate limiting
5. **Admin Panel** - Subsidy rules management
