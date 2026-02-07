# Ground Truth Test Cases for Yield Calculation Accuracy

These 10 test cases are engineer-validated calculations for verifying RainForge accuracy (±10% tolerance).

## Calculation Formula

```
Annual Yield (L) = Roof Area (m²) × Annual Rainfall (m) × Runoff Coefficient
Monthly Yield (L) = Roof Area (m²) × Monthly Rainfall (m) × Runoff Coefficient
```

## Runoff Coefficients by Material
- Concrete: 0.85
- Metal/GI: 0.90
- Tiles: 0.75
- Thatched: 0.60

---

## Test Case Summaries

| ID | Location | Area (m²) | Rainfall (mm/yr) | Material | Coefficient | Expected Yield (L/yr) |
|----|----------|-----------|------------------|----------|-------------|----------------------|
| GT-001 | Delhi | 100 | 700 | Concrete | 0.85 | 59,500 |
| GT-002 | Mumbai | 150 | 2,200 | Metal | 0.90 | 297,000 |
| GT-003 | Bangalore | 200 | 970 | Tiles | 0.75 | 145,500 |
| GT-004 | Chennai | 250 | 1,400 | Concrete | 0.85 | 297,500 |
| GT-005 | Jaipur | 180 | 650 | Tiles | 0.75 | 87,750 |
| GT-006 | Hyderabad | 300 | 800 | Metal | 0.90 | 216,000 |
| GT-007 | Kolkata | 120 | 1,600 | Concrete | 0.85 | 163,200 |
| GT-008 | Pune | 400 | 1,100 | Concrete | 0.85 | 374,000 |
| GT-009 | Jodhpur (Arid) | 500 | 350 | Metal | 0.90 | 157,500 |
| GT-010 | Cherrapunji (High) | 100 | 11,777 | Tiles | 0.75 | 883,275 |

---

## Acceptance Criteria

For each test case, RainForge annual yield must be within ±10% of expected value:

```
Lower Bound = Expected × 0.90
Upper Bound = Expected × 1.10
```

| ID | Expected | Lower | Upper | Pass Condition |
|----|----------|-------|-------|----------------|
| GT-001 | 59,500 | 53,550 | 65,450 | ✓ if in range |
| GT-002 | 297,000 | 267,300 | 326,700 | ✓ if in range |
| GT-003 | 145,500 | 130,950 | 160,050 | ✓ if in range |
| GT-004 | 297,500 | 267,750 | 327,250 | ✓ if in range |
| GT-005 | 87,750 | 78,975 | 96,525 | ✓ if in range |
| GT-006 | 216,000 | 194,400 | 237,600 | ✓ if in range |
| GT-007 | 163,200 | 146,880 | 179,520 | ✓ if in range |
| GT-008 | 374,000 | 336,600 | 411,400 | ✓ if in range |
| GT-009 | 157,500 | 141,750 | 173,250 | ✓ if in range |
| GT-010 | 883,275 | 794,948 | 971,603 | ✓ if in range |
