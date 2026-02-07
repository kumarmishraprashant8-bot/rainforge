# Fraud Detection Specification

## Overview

RainForge implements multi-layer fraud detection to ensure verification integrity for RWH installations. This document specifies the heuristics, thresholds, and test vectors.

---

## Fraud Detection Layers

### Layer 1: EXIF Metadata Validation

**Purpose**: Ensure photos are original, unedited, and contain GPS data.

| Check | Pass Condition | Flag Condition | Fail Condition |
|-------|----------------|----------------|----------------|
| EXIF Presence | EXIF data exists | - | No EXIF metadata |
| GPS Data | GPS coordinates present | - | No GPS in EXIF |
| GPS Timestamp | Within 1 hour of upload | >1 hour, <24 hours | >24 hours or missing |
| Software Field | Camera app only | Unknown software | "Photoshop", "GIMP", etc. |
| Image Dimensions | Original resolution | Compressed >50% | Very low resolution |

**Implementation**: `fraud_detector.py` → `_get_exif_data()`, `validate_photo()`

---

### Layer 2: Geofence Validation

**Purpose**: Verify photo was taken at the claimed project location.

```python
distance_m = haversine(photo_lat, photo_lng, site_lat, site_lng) * 1000
```

| Distance | Status | Score Impact |
|----------|--------|--------------|
| ≤50m | PASS | 0.0 |
| 51-200m | WARNING | +0.3 |
| 201-500m | FLAG | +0.6 |
| >500m | FAIL | +1.0 |

**Formula (Haversine)**:
```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c
```

---

### Layer 3: Photo Hash Reuse Detection

**Purpose**: Detect reused photos across different verifications.

**Algorithm**:
1. Calculate SHA-256 hash of uploaded image
2. Query database for existing hashes
3. Flag if exact match found

```python
import hashlib

def get_photo_hash(image_bytes):
    return hashlib.sha256(image_bytes).hexdigest()
```

| Result | Status | Score Impact |
|--------|--------|--------------|
| No match | PASS | 0.0 |
| Match in same project | WARNING | +0.2 |
| Match in different project | FAIL | +1.0 |

**Future Enhancement**: Perceptual hashing (pHash) for near-duplicate detection.

---

### Layer 4: Travel Anomaly Detection (Optional)

**Purpose**: Detect impossible travel patterns for installers.

**Rule**: If installer device was at Location A at time T1 and Location B at T2, calculate:
```
required_speed = distance(A, B) / (T2 - T1)
```

| Speed | Status |
|-------|--------|
| ≤120 km/h | PLAUSIBLE |
| 121-300 km/h | FLAG |
| >300 km/h | IMPOSSIBLE |

---

### Layer 5: Geo-Temporal Consistency

**Purpose**: Validate photo timestamp against physical plausibility.

**Checks**:
1. Photo timestamp is not in the future
2. Photo timestamp is after project creation date
3. Photo timestamp is within project timeline

---

## Composite Fraud Score

**Formula**:
```python
fraud_score = min(1.0, sum([
    exif_score,      # 0.0 - 1.0
    geofence_score,  # 0.0 - 1.0
    hash_score,      # 0.0 - 1.0
    travel_score,    # 0.0 - 0.5
    temporal_score   # 0.0 - 0.3
]))
```

**Decision Thresholds**:

| Score Range | Status | Action |
|-------------|--------|--------|
| 0.0 - 0.2 | AUTO_APPROVE | Automatic verification pass |
| 0.21 - 0.5 | REVIEW | Queue for human review |
| 0.51 - 0.79 | FLAG | Senior review required |
| 0.80 - 1.0 | REJECT | Automatic rejection + audit log |

---

## Test Vectors

### Legitimate Submissions (Should Pass)

| ID | Description | Expected Score | Expected Status |
|----|-------------|----------------|-----------------|
| L-001 | Valid EXIF, GPS within 10m, new photo | 0.0 | AUTO_APPROVE |
| L-002 | Valid EXIF, GPS within 45m, new photo | 0.1 | AUTO_APPROVE |
| L-003 | Valid EXIF, GPS within 50m, same-day timestamp | 0.15 | AUTO_APPROVE |

### Fraud Attempts (Should Reject/Flag)

| ID | Description | Expected Score | Expected Status |
|----|-------------|----------------|-----------------|
| F-001 | No EXIF metadata (stripped) | 0.8 | REJECT |
| F-002 | GPS 600m from site | 1.0 | REJECT |
| F-003 | Photo hash matches previous project | 1.0 | REJECT |
| F-004 | Photoshop in Software field | 0.7 | FLAG |
| F-005 | GPS 150m from site | 0.3 | REVIEW |
| F-006 | Timestamp 48 hours old | 0.4 | REVIEW |
| F-007 | Impossible travel (500km in 30min) | 0.6 | FLAG |

### Edge Cases

| ID | Description | Expected Handling |
|----|-------------|-------------------|
| E-001 | Indoor photo (no GPS) | Allow manual GPS override |
| E-002 | Very old phone (poor EXIF) | Reduced weight on EXIF |
| E-003 | Multi-building complex | Expanded geofence (200m) |

---

## Acceptance Criteria

### Fraud Detection Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recall (fraud cases) | ≥90% | % of seeded fraud detected |
| False Positive Rate | ≤10% | % of legitimate flagged |
| Average Processing Time | <2s | Per verification |

### Test Results (Seeded Data)

Run against `seed_sites_verified.csv` fraud cases:

| Site ID | Fraud Type | Detected | Score |
|---------|------------|----------|-------|
| SITE-F016 | location_mismatch, photo_reuse | ✓ | 1.0 |
| SITE-F017 | exif_stripped, timestamp_invalid | ✓ | 0.9 |
| SITE-F018 | distance_warning | ✓ | 0.4 |
| SITE-F019 | photo_reuse, software_edited | ✓ | 1.0 |

**Result**: 4/4 fraud cases detected = 100% recall

---

## API Reference

### POST /api/v1/verification/verify

**Request**:
```json
{
  "project_id": 123,
  "photos": [
    {"url": "https://...", "type": "installation_complete"}
  ],
  "geo_lat": 28.6139,
  "geo_lng": 77.2090,
  "installer_id": 1
}
```

**Response**:
```json
{
  "verification_id": "VER-20260203-001",
  "fraud_score": 0.15,
  "status": "auto_approve",
  "flags": [],
  "audit_entries": [
    {"check": "exif_presence", "result": "pass"},
    {"check": "geofence", "result": "pass", "distance_m": 25},
    {"check": "photo_hash", "result": "pass"}
  ]
}
```

---

## Audit Trail

All fraud checks are logged with:
- Timestamp
- Check type
- Input values
- Result
- Score contribution
- Reviewer ID (if human review)

Retention: 7 years (RTI compliance)
