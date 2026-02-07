# RainForge Architecture

**Owners**: Prashant Mishra & Ishita Parmar

---

## System Overview

```mermaid
flowchart TB
    subgraph Users
        WEB[Web Browser]
        MOBILE[Mobile App]
        IOT[IoT Sensors]
    end
    
    subgraph "Load Balancer"
        NGINX[Nginx]
    end
    
    subgraph "Application Layer"
        FE[React Frontend]
        API[FastAPI Backend]
        ML[ML Service]
        WORKER[Celery Workers]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL + PostGIS)]
        TS[(TimescaleDB)]
        REDIS[(Redis)]
        MINIO[(MinIO S3)]
    end
    
    subgraph "External APIs"
        IMD[IMD Rainfall]
        OWM[OpenWeatherMap]
        MAPBOX[Mapbox]
    end
    
    WEB --> NGINX
    MOBILE --> NGINX
    IOT --> NGINX
    
    NGINX --> FE
    NGINX --> API
    NGINX --> ML
    
    FE --> API
    API --> PG
    API --> TS
    API --> REDIS
    API --> MINIO
    API --> ML
    API --> WORKER
    
    WORKER --> PG
    WORKER --> REDIS
    WORKER --> MINIO
    
    ML --> PG
    
    API --> IMD
    API --> OWM
    API --> MAPBOX
```

---

## Component Details

### Frontend (React + TypeScript)
- **Location**: `/frontend`
- **Features**:
  - Assessment wizard with map drawing
  - Monitoring dashboard with charts
  - Bulk upload with progress tracking
  - Verification photo capture

### Backend (FastAPI + Python)
- **Location**: `/backend`
- **Key Services**:
  - `calculation_engine.py` - RWH formulas
  - `assessments.py` - Quick/complete assessments
  - `bulk_api.py` - CSV processing
  - `monitoring_api.py` - Sensor ingestion

### ML Service
- **Location**: `/backend/app/ml`
- **Models**:
  - Image verification (MobileNetV2)
  - Capture prediction (weather-based)
  - Explainability endpoints

### Worker (Celery)
- **Location**: `/backend/app/worker`
- **Tasks**:
  - Bulk CSV processing
  - PDF generation
  - ML inference
  - Geocoding

---

## Data Flow

### Assessment Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant C as Calculation Engine
    participant D as Database
    
    U->>F: Enter roof details
    F->>A: POST /api/assessments/quick
    A->>C: run_full_assessment()
    C->>C: Calculate yield, tank, cost
    C->>A: Return results
    A->>D: Save assessment
    A->>F: Return assessment JSON
    F->>U: Display results
```

### Bulk Processing Flow
```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant R as Redis
    participant W as Celery Worker
    participant D as Database
    
    U->>A: POST /api/bulk/upload (CSV)
    A->>R: Queue job
    A->>U: Return job_id
    R->>W: Process job
    W->>D: Process each row
    W->>D: Generate PDFs
    W->>R: Update status
    U->>A: GET /api/bulk/status/{job_id}
    A->>R: Get status
    A->>U: Return progress
```

### IoT Monitoring Flow
```mermaid
sequenceDiagram
    participant S as Sensor
    participant M as MQTT Broker
    participant A as API
    participant T as TimescaleDB
    participant F as Frontend
    
    S->>M: Publish reading
    M->>A: Forward to worker
    A->>T: Store in hypertable
    F->>A: GET /monitoring/{id}/status
    A->>T: Query latest data
    A->>F: Return status
```

---

## Database Schema

### Core Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts and auth |
| `organizations` | Tenant organizations |
| `projects` | RWH project sites |
| `assessments` | Calculation results |
| `sensors` | IoT device registry |
| `monitoring_data` | Time-series readings |
| `verifications` | Photo verifications |
| `audit_log` | Immutable audit trail |

### Key Indexes

```sql
-- Spatial queries
CREATE INDEX idx_projects_geom ON projects USING GIST(roof_geom);

-- Time-series queries
SELECT create_hypertable('monitoring_data', 'timestamp');

-- Audit queries
CREATE INDEX idx_audit_project ON audit_log(entity_type, entity_id);
```

---

## Security Architecture

```mermaid
flowchart LR
    subgraph Public
        USER[Users]
    end
    
    subgraph DMZ
        NGINX[Nginx WAF]
    end
    
    subgraph Private
        API[Backend]
        DB[(Database)]
    end
    
    USER -->|HTTPS| NGINX
    NGINX -->|Rate Limited| API
    API -->|TLS| DB
```

### Security Measures
- JWT authentication for users
- API keys for sensors
- HTTPS everywhere
- Rate limiting (10 req/sec)
- Input validation
- SQL injection prevention
- CSRF protection
- Audit logging

---

## Scalability

### Horizontal Scaling
- Stateless API containers
- Redis-backed sessions
- S3-compatible file storage
- Load balancer (Nginx)

### Performance Targets
| Metric | Target |
|--------|--------|
| Quick Assessment | < 500ms |
| Bulk (1000 rows) | < 60s |
| Sensor Ingestion | < 50ms |
| PDF Generation | < 5s |

---

## Deployment

### Docker Compose (Development)
```bash
docker-compose up --build
```

### Kubernetes (Production)
- Helm charts in `/k8s`
- Horizontal Pod Autoscaling
- PostgreSQL operator
- Ingress with TLS

---

## Monitoring

### Prometheus Metrics
- Request latency
- Error rates
- Queue depth
- Database connections

### Grafana Dashboards
- API performance
- Worker queue
- Database health
- Business metrics

---

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL, PostGIS, TimescaleDB |
| Cache | Redis |
| Storage | MinIO (S3) |
| Queue | Celery, Redis |
| ML | TensorFlow/PyTorch |
| Proxy | Nginx |
| Containers | Docker, Kubernetes |
