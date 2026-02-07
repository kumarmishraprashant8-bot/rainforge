# RainForge — Government Language & Terminology Guide

## Purpose
Ensure all UI labels, API responses, and documentation use government-friendly language.
No dev jargon. No AI hallucination language. Clear units everywhere.

---

## Label Replacements

| ❌ Don't Use | ✅ Use Instead |
|--------------|----------------|
| ML model | Assessment algorithm |
| AI-powered | Automated calculation |
| Neural network | Pattern detection |
| Prediction | Estimation |
| Black box | Transparent formula |
| API call | Data retrieval |
| Backend | System |
| Frontend | Portal |
| Database | Records |
| Webhook | Automatic notification |
| Payload | Data |
| JSON | Report format |
| UUID | Reference number |
| Timestamp | Date and time |
| Boolean | Yes/No |
| Null/None | Not available |
| Localhost | Demo server |
| Deployment | Installation |
| Container | Service |
| Latency | Response time |
| Error 500 | System temporarily unavailable |
| Timeout | Request taking longer than expected |

---

## Unit Standards (Always Include)

| Measurement | Format | Example |
|-------------|--------|---------|
| Money | ₹X,XX,XXX | ₹1,25,000 |
| Volume (small) | X litres | 5,000 litres |
| Volume (large) | X kilolitres | 150 kilolitres |
| Area | X m² | 120 m² |
| Rainfall | X mm | 850 mm/year |
| Distance | X km | 2.5 km |
| Time duration | X days/hours | 48 hours |
| Percentage | X% | 45% |
| Weight | X kg | 8,500 kg |

**Never show raw decimal values** (e.g., 0.85 → "85%")

---

## Status Labels (Government Style)

| Internal Status | Display Label |
|-----------------|---------------|
| pending | Under Review |
| approved | Approved |
| rejected | Not Approved |
| in_progress | In Progress |
| completed | Completed |
| failed | Requires Attention |
| error | Unable to Process |
| queued | Scheduled |
| draft | Draft |
| expired | Validity Expired |

---

## Confidence Grade Explanations (For Citizens)

| Grade | Display | Citizen-Friendly Meaning |
|-------|---------|--------------------------|
| A | Excellent | Highly reliable assessment based on official data |
| B | Good | Reliable assessment, minor verification recommended |
| C | Moderate | Preliminary estimate, site visit recommended |
| D | Limited | Rough estimate only, professional consultation needed |
| F | Insufficient | Cannot provide reliable assessment |

---

## Subsidy Language

| ❌ Avoid | ✅ Use |
|---------|-------|
| Discount | Subsidy |
| Free money | Government assistance |
| Claim | Apply for |
| Get paid | Receive subsidy |
| Cashback | Subsidy reimbursement |

---

## Technical Terms → Government Terms

| Technical | Government |
|-----------|------------|
| Runoff coefficient | Water collection efficiency |
| First-flush diverter | Initial rainwater separator |
| pHash detection | Photo verification check |
| Geo-mismatch | Location verification |
| Escrow | Secure payment holding |
| RPI score | Installer Performance Rating |
| Fraud score | Risk assessment |
| SLA breach | Delayed delivery |
| Blacklist | Suspended from scheme |

---

## Document Titles

| Internal | Official Title |
|----------|----------------|
| Assessment PDF | Rainwater Harvesting Assessment Certificate |
| Verification report | Installation Verification Report |
| Invoice | Cost Estimate Statement |
| Audit log | Project Transaction History |
| Dashboard | Scheme Progress Dashboard |

---

## Error Messages (Graceful)

| ❌ Technical | ✅ User-Friendly |
|--------------|------------------|
| 404 Not Found | The requested information is not available. Please check the reference number. |
| 500 Server Error | Our system is currently undergoing maintenance. Please try again in a few minutes. |
| Timeout | Your request is taking longer than expected. We are working on it. |
| Invalid input | Please check the information entered and try again. |
| Authentication failed | Please log in again to continue. |
| Rate limited | Too many requests. Please wait a moment before trying again. |

---

## Disclaimer Templates

### Assessment Disclaimer
> This assessment is based on [IMD/estimated] rainfall data and user-provided measurements. Actual performance may vary. Final installation should be supervised by a certified professional as per IS 15797:2018.

### Subsidy Disclaimer
> Subsidy amounts and eligibility are subject to state government scheme rules. RainForge provides estimates only. Please verify with the official portal before proceeding.

### Projection Disclaimer
> SCENARIO PROJECTION — The figures shown are based on stated assumptions and are for planning purposes only. Actual outcomes depend on real-world implementation.

---

## Quality Checklist

- [ ] All ₹ amounts include commas (₹1,25,000 not ₹125000)
- [ ] All volumes have units (litres, kilolitres)
- [ ] All areas have units (m²)
- [ ] No "undefined" or "null" visible in UI
- [ ] No error codes visible to users
- [ ] All dates in DD-MM-YYYY format
- [ ] All percentages rounded to 1 decimal
- [ ] No technical jargon in citizen-facing views
- [ ] All downloadable files have meaningful names
- [ ] QR codes are large enough to scan
