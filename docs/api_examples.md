# RainForge API Examples

HTTPie and cURL examples for key endpoints.

## Multi-modal assessment (Feature A)

Create an assessment with optional input mode. Response includes `pdf_url` and `confidence`.

### Address mode (full details)

```bash
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Gandhi Road, New Delhi",
    "mode": "address",
    "lat": 28.6139,
    "lng": 77.2090,
    "roof_area_sqm": 120,
    "roof_material": "concrete",
    "state": "Delhi",
    "city": "New Delhi"
  }'
```

```bash
http POST http://localhost:8000/api/v1/assessments \
  address="123 Gandhi Road, New Delhi" \
  mode=address \
  lat:=28.6139 lng:=77.2090 \
  roof_area_sqm:=120 \
  state=Delhi city="New Delhi"
```

### Satellite-only mode (fallbacks when site details missing)

```bash
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"address":"seeded address","mode":"satellite-only"}'
```

### Photo mode (image-based assessment)

```bash
curl -X POST http://localhost:8000/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{"address":"Photo site","mode":"photo"}'
```

### Response (200)

```json
{
  "assessment_id": "ASM-20260207-ABC123",
  "site_id": "SITE-...",
  "address": "...",
  "mode": "address",
  "annual_rainfall_mm": 700,
  "annual_yield_liters": 71400,
  "scenarios": { "cost_optimized": {...}, "max_capture": {...}, "dry_season": {...} },
  "recommended_scenario": "max_capture",
  "confidence": 85.0,
  "pdf_url": "/api/v1/assess/ASM-20260207-ABC123/pdf",
  "verify_url": "/api/v1/verify/<uuid>",
  "created_at": "2026-02-07T..."
}
```

## Existing assessment (unchanged)

```bash
curl -X POST "http://localhost:8000/api/v1/assess?site_id=SITE001&address=123%20Demo%20St&lat=28.6139&lng=77.209&roof_area_sqm=120&roof_material=concrete&floors=1&people=4&state=Delhi&city=New%20Delhi"
```

## Download assessment PDF

```bash
curl -O -J "http://localhost:8000/api/v1/assess/ASM-20260207-ABC123/pdf"
```
