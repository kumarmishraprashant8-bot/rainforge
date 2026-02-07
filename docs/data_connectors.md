# RainForge Data Connectors

## Overview
This document specifies all external data sources used by RainForge, with production endpoints and fallback mechanisms.

---

## 1. Rainfall Data

### Primary: India Meteorological Department (IMD)
- **Endpoint**: `https://imd.gov.in/api/gridded/rainfall` (hypothetical - requires registration)
- **Data Type**: Gridded monthly rainfall (0.25° resolution)
- **Format**: NetCDF / CSV
- **Update Frequency**: Daily
- **Authentication**: API Key (apply at imd.gov.in)

### Secondary: CHIRPS (Climate Hazards Group)
- **Endpoint**: `https://data.chc.ucsb.edu/products/CHIRPS-2.0/`
- **Data Type**: Global monthly precipitation
- **Format**: NetCDF / GeoTIFF
- **Resolution**: 0.05° (~5km)
- **Access**: Public (no auth required)
- **Example**: `chirps-v2.0.2025.01.tif`

### Fallback: Open-Meteo API
- **Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Parameters**:
  ```
  ?latitude={lat}&longitude={lng}
  &start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}
  &daily=precipitation_sum
  ```
- **Rate Limit**: 10,000 requests/day (free tier)
- **Authentication**: None required

### Implementation Status
- [x] Open-Meteo integration (primary for demo)
- [x] Mock IMD data for offline demo
- [ ] CHIRPS NetCDF parser (optional)

---

## 2. Weather Forecast

### Open-Meteo Forecast API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Parameters**:
  ```
  ?latitude={lat}&longitude={lng}
  &daily=precipitation_sum,precipitation_probability_max
  &forecast_days=14
  ```
- **Update Frequency**: Hourly
- **Rate Limit**: 10,000 requests/day

### Implementation Status
- [x] 7-day forecast integration
- [x] Overflow prediction using forecast

---

## 3. Geocoding & Maps

### Primary: Nominatim (OpenStreetMap)
- **Endpoint**: `https://nominatim.openstreetmap.org/search`
- **Parameters**: `?q={address}&format=json&limit=1`
- **Rate Limit**: 1 request/second
- **Authentication**: None (respect usage policy)

### Map Tiles: OpenStreetMap
- **Endpoint**: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- **Usage**: Leaflet/Mapbox GL JS integration
- **License**: ODbL

### Implementation Status
- [x] Nominatim geocoding
- [x] OSM tiles for map display
- [x] Polygon drawing on map

---

## 4. Elevation Data

### AWS Terrain Tiles (SRTM)
- **Endpoint**: `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`
- **Resolution**: 30m
- **Format**: Terrarium encoding (RGB)
- **Usage**: Slope calculation, drainage analysis

### Implementation Status
- [ ] Not implemented (optional enhancement)
- [x] User-input slope fallback

---

## 5. Subsidy Rules

### Configuration File
- **Location**: `data/subsidy_rules.csv`
- **Schema**:
  ```csv
  state,scheme_name,subsidy_pct,max_subsidy_inr,eligible_building_types,min_roof_sqm,max_roof_sqm,valid_from,valid_until,source_url
  ```
- **Update Frequency**: Annual (manual update)

### Official Sources
| State | Source URL |
|-------|------------|
| Delhi | https://delhijalboard.nic.in |
| Maharashtra | https://mahawater.gov.in |
| Karnataka | https://bwssb.gov.in |
| Tamil Nadu | https://tnpwd.gov.in |
| Telangana | https://hyderabadwater.gov.in |

### Implementation Status
- [x] CSV-based subsidy lookup
- [x] State-wise calculation

---

## 6. Installer Registry

### Configuration File
- **Location**: `data/seed_installers.csv`
- **Schema**:
  ```csv
  installer_id,name,company,lat,lng,rpi_score,capacity_available,capacity_max,avg_cost_factor,sla_compliance_pct,jobs_completed,is_blacklisted,cert_level,service_areas,warranty_months,specialization
  ```

### In Production
- Database table with CRUD operations
- Admin portal for registration approval
- Automated RPI recalculation

### Implementation Status
- [x] CSV seed data for demo
- [x] RPI calculation service
- [x] Allocation engine

---

## 7. IoT Telemetry

### MQTT Broker
- **Endpoint**: `mqtt://localhost:1883` (demo)
- **Topic Pattern**: `rainforge/{project_id}/sensors/{device_type}`
- **Payload Schema**:
  ```json
  {
    "device_id": "DEV-001",
    "timestamp": "2026-02-03T12:00:00Z",
    "value": 3500,
    "unit": "liters",
    "battery_pct": 92,
    "signal_rssi": -45
  }
  ```

### HTTP Webhook Alternative
- **Endpoint**: `POST /api/v1/telemetry/ingest`
- **Auth**: Bearer token

### Implementation Status
- [x] MQTT client service
- [x] HTTP webhook endpoint
- [x] Simulated telemetry for demo

---

## 8. Payment Gateway

### Mock Adapter (Demo)
- Uses in-memory escrow simulation
- Milestone-based release

### Production Integration
| Provider | Integration Type |
|----------|------------------|
| Razorpay | REST API |
| PayU | REST API |
| Stripe India | REST API |

### Implementation Status
- [x] Mock payment adapter
- [x] Escrow milestone flow
- [ ] Production payment integration

---

## Environment Variables

```env
# Rainfall APIs
OPENMETEO_API_URL=https://api.open-meteo.com/v1
IMD_API_KEY=your_imd_api_key_here

# Maps
NOMINATIM_URL=https://nominatim.openstreetmap.org

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=rainforge
MQTT_PASSWORD=your_password

# Payments (Production)
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

---

## Fallback Strategy

| Data Source | Primary | Fallback 1 | Fallback 2 |
|-------------|---------|------------|------------|
| Rainfall | IMD API | Open-Meteo | Static CSV |
| Forecast | Open-Meteo | OpenWeather | 30-year avg |
| Geocoding | Nominatim | Google Maps | Manual input |
| Maps | OSM | Mapbox | Static image |
| Telemetry | MQTT | HTTP webhook | Manual entry |
| Payments | Razorpay | PayU | Bank transfer |
