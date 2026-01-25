# Municipal RWH Pilot Playbook
**Deploying RainForge for 10,000 Households**

---

## Executive Summary

RainForge enables municipal governments to:
- **Allocate** installers optimally using data-driven scoring
- **Procure** through transparent competitive bidding
- **Pay** via milestone-based escrow (fraud-resistant)
- **Verify** installations with geo-tagged photos + fraud detection
- **Report** real-time to citizens via public dashboard

---

## Phase 1: Preparation (Week 1-2)

### 1.1 Data Collection
- [ ] Ward boundaries GeoJSON
- [ ] Municipal building inventory (schools, hospitals, offices)
- [ ] Existing RWH installations database
- [ ] Approved installer list with certifications

### 1.2 System Setup
```bash
# Deploy with Docker
docker-compose up --build

# Run database migrations
psql -d rainforge -f db/migrations/001_marketplace.sql

# Seed demo data
psql -d rainforge -f db/seed_demo_data.sql
```

### 1.3 Installer Onboarding
1. Register installers via admin panel
2. Collect: Company details, certifications, coverage area
3. Initial RPI set to 70 (neutral)
4. Training on photo verification requirements

---

## Phase 2: Pilot Launch (Week 3-4)

### 2.1 Site Selection
- 100 priority sites (schools, hospitals)
- Geographic distribution across 5+ wards
- Mix of building sizes (50-500 m² roof area)

### 2.2 Allocation Strategy
```
Mode: Gov Optimized
Weights:
  - RPI: 35%
  - SLA History: 25%
  - Capacity: 20%
  - Distance: 15%
  - Cost: 5%
```

### 2.3 Bidding Process
1. Open bidding for 72 hours per job batch
2. Minimum 3 bids required
3. Auto-ranking by composite score
4. Award to top-ranked unless manual override

---

## Phase 3: Execution (Week 5-12)

### 3.1 Milestone Workflow
| Milestone | Trigger | Payment % |
|-----------|---------|-----------|
| Design Approval | Survey + design submitted | 20% |
| Installation Complete | Installer marks done | 40% |
| Verification Passed | Admin approves photos | 30% |
| Post-Performance | 30-day yield check | 10% |

### 3.2 Verification Checklist
- [ ] Tank installed at marked location
- [ ] First-flush diverter present
- [ ] Overflow connected to recharge pit
- [ ] Photo shows all components
- [ ] Geo-tag within 100m of site

### 3.3 Fraud Prevention
- Random 10% field audits
- Photo hash comparison across all submissions
- Geo-temporal anomaly detection (impossible travel)
- RPI impact for failed verifications

---

## Phase 4: Scaling (Month 4-12)

### 4.1 Batch Operations
- CSV upload for 100+ sites at once
- Bulk allocation runs nightly
- Automated bid opening by schedule

### 4.2 AMC Enrollment
- Gold tier for public buildings (₹8,500/yr)
- Silver tier for residential (₹5,000/yr)
- Auto-renewal with 30-day reminder

### 4.3 Outcome Contracts
For premium installations:
- Target: 80% of predicted yield
- Monitoring: IoT sensors or monthly manual reads
- Payment: Final 10% released only if target met

---

## Metrics & Reporting

### Daily Dashboard
- Jobs in progress
- Pending verifications
- Escrow balance
- Fraud alerts

### Weekly Report
- New allocations
- Bids awarded
- Funds released
- RPI changes

### Monthly Transparency
- Public dashboard update
- Ward-wise capture data
- CO₂ avoided estimate
- Investment ROI

---

## Budget Template (10,000 Households)

| Item | Unit Cost | Quantity | Total |
|------|-----------|----------|-------|
| Average RWH System | ₹50,000 | 10,000 | ₹50 Cr |
| Platform License | ₹5/site/yr | 10,000 | ₹0.5L/yr |
| Field Verification | ₹200/site | 10,000 | ₹20L |
| Admin Staff (5) | ₹40K/mo | 12 mo | ₹24L |
| **Total First Year** | | | **₹50.7 Cr** |

### Subsidy Sources
- Jal Shakti Abhiyan: Up to 50% (₹25 Cr)
- State RWH Scheme: Up to 30% (₹15 Cr)
- Net Municipal Investment: ₹10.7 Cr

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Installer fraud | Multi-layer verification + RPI penalties |
| Payment disputes | Escrow with clear milestones |
| Low adoption | Public dashboard showing neighbor success |
| Technical failure | Offline-capable mobile app (roadmap) |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Installation completion rate | >95% |
| Verification pass rate | >90% |
| Average time to install | <30 days |
| Citizen satisfaction | >4.2/5 |
| Water captured | >500M L/year |

---

## Support

- **Technical:** tech@rainforge.in
- **Procurement:** procurement@rainforge.in
- **Training:** training@rainforge.in

---

*RainForge Pilot Playbook v1.0*
*Jal Shakti Abhiyan Aligned*
