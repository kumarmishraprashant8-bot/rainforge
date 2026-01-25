# RainForge Admin Runbook

## Table of Contents
1. [Allocation Weight Tuning](#allocation-weight-tuning)
2. [Bid Management](#bid-management)
3. [Payment Releases](#payment-releases)
4. [Verification Review](#verification-review)
5. [Fraud Handling](#fraud-handling)
6. [Installer Management](#installer-management)

---

## Allocation Weight Tuning

### Default Weights
| Factor | Weight | Description |
|--------|--------|-------------|
| RPI | 30% | Installer performance index |
| Capacity | 20% | Available workload slots |
| Cost Band | 20% | Price competitiveness |
| Distance | 15% | Proximity to job site |
| SLA History | 15% | Past delivery performance |

### When to Adjust

**Increase RPI weight when:**
- Quality issues reported in district
- Post-monsoon season (need reliable completion)

**Increase Capacity weight when:**
- Large backlog of jobs
- Equitable distribution mandated

**Increase Distance weight when:**
- Rural/remote areas
- Emergency repairs

### API Command
```bash
curl -X PUT http://localhost:8000/api/v1/marketplace/allocation-weights \
  -H "Content-Type: application/json" \
  -d '{"capacity": 0.25, "rpi": 0.35, "cost_band": 0.15, "distance": 0.15, "sla_history": 0.10}'
```

---

## Bid Management

### Opening Bids
```bash
curl -X POST http://localhost:8000/api/v1/marketplace/jobs/116/open-bid \
  -H "Content-Type: application/json" \
  -d '{"deadline_hours": 72}'
```

### Awarding Bids
1. Navigate to Marketplace → Competitive Bidding
2. Review ranked bids (auto-scored)
3. Click "Award Bid" on selected installer
4. Confirmation triggers job assignment

### Bid Score Components
- **Price (35%):** Lower = better
- **Timeline (20%):** Faster = better
- **Warranty (15%):** Longer = better
- **RPI (30%):** Higher = better

---

## Payment Releases

### Milestone Sequence
1. **Design Approval (20%)** - After site survey approved
2. **Installation Complete (40%)** - After physical work done
3. **Verification Passed (30%)** - After admin verification
4. **Post-Performance (10%)** - After 30-day check

### Release Process
1. Installer marks milestone complete
2. Admin verifies (site visit or photo review)
3. Admin releases funds
4. System transfers from escrow to installer

### Emergency Refund
```bash
curl -X POST http://localhost:8000/api/v1/payments/PAY-001/refund \
  -d "reason=Project cancelled"
```

---

## Verification Review

### Pending Queue
Navigate to: `/verification` or API:
```bash
curl http://localhost:8000/api/v1/verify/pending
```

### Review Checklist
- [ ] Photo shows completed installation
- [ ] Geo location within 100m of site
- [ ] Timestamp within 24h of claimed completion
- [ ] No fraud flags

### Approval
```bash
curl -X POST http://localhost:8000/api/v1/verify/VER-001/approve
```

### Rejection with Rework
```bash
curl -X POST http://localhost:8000/api/v1/verify/VER-001/reject \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected", "require_rework": true, "verifier_notes": "Tank position incorrect"}'
```

---

## Fraud Handling

### Fraud Flags
| Flag | Severity | Action |
|------|----------|--------|
| Photo Reuse | HIGH | Immediate review, possible blacklist |
| Geo Mismatch >500m | HIGH | Site visit required |
| Geo Mismatch 100-500m | MEDIUM | Phone verification |
| Timestamp Anomaly | HIGH | Check with GPS data |
| Metadata Issues | LOW | Document, monitor |

### Blacklist Installer
```sql
UPDATE installers SET is_blacklisted = TRUE, blacklist_reason = 'Fraud detected: photo reuse' WHERE id = 8;
```

### Audit Trail
All fraud flags stored in `verifications.fraud_flags` JSON column.

---

## Installer Management

### View RPI
```bash
curl http://localhost:8000/api/v1/marketplace/installers/1/rpi
```

### RPI Components
| Metric | Weight | Data Source |
|--------|--------|-------------|
| Design Match % | 25% | Verification comparison |
| Yield Accuracy % | 25% | IoT monitoring vs predicted |
| Timeliness Score | 20% | Job completion records |
| Complaint Rate | 15% | Citizen feedback |
| Maintenance Compliance | 15% | AMC visit logs |

### Suspension Triggers
- RPI < 50 for 3 consecutive months
- 2+ fraud flags in 6 months
- Failed audit

---

## Escalation Contacts

| Issue | Contact |
|-------|---------|
| Payment Stuck | finance@rainforge.in |
| Fraud Alert | audit@rainforge.in |
| System Down | tech@rainforge.in |

---

*RainForge Admin Runbook v1.0*
