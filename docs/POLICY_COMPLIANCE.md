# RainForge — Standards & Policy Compliance

## Alignment with Government Standards

RainForge is designed to comply with national standards and mission objectives for rainwater harvesting. This document maps each requirement to the corresponding RainForge feature.

---

## 1. IS 15797:2018 — Rooftop Rainwater Harvesting Design

| Standard Requirement | RainForge Feature |
|---------------------|-------------------|
| §4.1 Catchment area calculation | Roof area input with material-based runoff coefficient (0.85-0.95) |
| §4.2 Rainfall data from IMD | IMD gridded rainfall data (25+ cities) with Open-Meteo fallback |
| §4.3 Storage capacity sizing | Tank sizing formula: `Area × Annual Rainfall × Runoff Coeff × Factor` |
| §4.4 First-flush diverter | Included in component cost breakdown (₹2,500-5,000) |
| §4.5 Filter specifications | Charcoal/sand filter costed in bill of materials |
| §4.6 Overflow arrangements | Overflow pipe included in design recommendations |
| §5.1 Quality of materials | Installer certification (MSME/Govt registered) verified |
| §5.2 Installation supervision | ML-based photo verification + geo-tagged proof |

---

## 2. CGWB Rainwater Harvesting Guidelines

| CGWB Guideline | RainForge Implementation |
|----------------|--------------------------|
| Site suitability assessment | GPS-based site validation + ward boundary check |
| Groundwater recharge potential | CGWB well-level data integration (8 major cities) |
| Aquifer mapping | Ward-level groundwater stress indicators |
| Recharge structure design | Recharge pit option in system design |
| Water quality monitoring | First-flush + filtration recommendations |
| Community awareness | Public transparency dashboard for citizen access |

---

## 3. Jal Shakti Abhiyan Objectives

| JSA Objective | RainForge Contribution |
|---------------|------------------------|
| Water conservation | Quantified water capture per installation (L/year) |
| Rainwater harvesting promotion | Free assessment tool + subsidy calculator |
| Traditional water body restoration | Ward-level impact aggregation |
| Intensive afforestation | CO₂ avoided calculation (kg/year) |
| Awareness programs | Public dashboard with project statistics |

---

## 4. AMRUT 2.0 — Urban Water Resilience

| AMRUT 2.0 Component | RainForge Mapping |
|---------------------|-------------------|
| 100% coverage of water supply | Self-sufficiency % calculation per site |
| Rejuvenation of water bodies | Recharge contribution estimation |
| Green spaces & parks | Institutional (school/hospital) priority scoring |
| Climate-resilient infrastructure | 5-year projection + flood mitigation metrics |
| Digital governance | Full audit trail, QR verification, officer logs |

**Export Format**: AMRUT-compatible JSON/CSV for municipal dashboard integration.

---

## 5. Jal Jeevan Mission — Sustainability & Monitoring

| JJM Requirement | RainForge Feature |
|-----------------|-------------------|
| Functional tap connections | Self-sufficiency days calculation |
| Water quality monitoring | Potable/non-potable design differentiation |
| IoT-based monitoring | MQTT telemetry + tank level dashboard |
| Community participation | Citizen complaint portal (5-level escalation) |
| Sustainability metrics | Maintenance scheduling + degradation prediction |

**Export Format**: JJM-compatible reporting for district-level integration.

---

## Certification & Audit Readiness

| Audit Requirement | RainForge Compliance |
|-------------------|---------------------|
| Data provenance | Rainfall source cited on every assessment |
| Calculation transparency | "How this was calculated" panel on every output |
| Officer accountability | Immutable decision log with timestamps |
| Financial traceability | Escrow milestones with release history |
| Anti-fraud measures | pHash + geo-mismatch + travel anomaly detection |

---

## Contact

For compliance queries: **compliance@rainforge.in**

Document Version: 1.0 | Last Updated: February 2026
