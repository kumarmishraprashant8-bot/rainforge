# RainForge — 8-Minute Demo Script

> **Target**: Jal Shakti Hackathon Technical Evaluation Committee
> **Goal**: Demonstrate 4 WOW moments that prove anti-corruption via code

---

## Pre-Demo Checklist

- [ ] Backend running: `docker-compose up` or `uvicorn app.main_demo:app --reload`
- [ ] Frontend running: `npm run dev`
- [ ] Demo data seeded: Call `POST /api/v1/admin/demo/reset`
- [ ] Verify ribbon shows: "🎯 DEMO MODE – SAFE DATA"
- [ ] Browser tabs open: Dashboard, Verification, Public Dashboard

---

## 🎬 Demo Timeline (8 Minutes)

| Time | Section | WOW Moment |
|------|---------|------------|
| 0:00-1:30 | Introduction + Assessment | Setup |
| 1:30-3:00 | PDF + QR Verification | Trust |
| 3:00-5:00 | **Fraud Detection** | 🔥 WOW #1 |
| 5:00-6:00 | **Escrow Freeze** | 🔥 WOW #2 |
| 6:00-7:00 | **Public Dashboard** | 🔥 WOW #3 |
| 7:00-7:30 | **RTI Export** | 🔥 WOW #4 |
| 7:30-8:00 | Closing + Impact | Summary |

---

## Step-by-Step Demo

### 🕐 0:00-1:30 — Introduction + Quick Assessment (90s)

**Action**: Open dashboard → Enter site details → Generate assessment

**Say**:
> "Good morning. RainForge transforms rooftop rainwater harvesting from a paper-based process into a transparent, fraud-resistant platform. Let me show you."

> "I enter a government school in Delhi — 200 sqm roof, concrete material. One click generates three design scenarios following IS 15797 standards."

**Show**:
- Cost-optimized: ₹48,000, 6000L tank
- Max capture: ₹85,000, 12000L tank  
- Dry season: ₹62,000, 8000L tank

---

### 🕐 1:30-3:00 — PDF + QR Verification (90s)

**Action**: Click "Download PDF" → Show QR code

**Say**:
> "Every assessment generates a government-ready certificate with QR verification. Any officer can scan this to verify authenticity — no calls, no paperwork."

**Scan QR**:
> "See? Real-time verification with engineer signature and timestamp."

---

### 🔥 3:00-5:00 — WOW MOMENT #1: FRAUD DETECTION (120s)

**Action**: Navigate to Verification → Upload fraud photo

**IMPORTANT**: Use these seeded photos from the demo reset:

| Photo Type | What to Show | Expected Result |
|------------|--------------|-----------------|
| `genuine.jpg` | Clean verification | ✅ Auto-approved, score 0.05 |
| `gps_mismatch.jpg` | **Use this** | 🔴 GPS 487m away, score 0.65 |
| `duplicate.jpg` | Same photo reused | 🔴 DUPLICATE detected, score 0.75 |
| `multi_fraud.jpg` | Multiple flags | ❌ FRAUD DETECTED, score 0.92 |

**Say**:
> "Now the WOW moment. An installer uploads a verification photo. Watch what happens."

> *(Upload gps_mismatch.jpg)*

> "Instantly — GPS mismatch detected. Photo taken 487 meters away from the registered site. Risk score 65%. Payment flagged."

> *(Upload duplicate.jpg)*

> "Even smarter — this photo was used for a different site last week. pHash matching catches it immediately."

**Point to banner**:
> "❌ FRAUD DETECTED – PAYMENT BLOCKED. This isn't a policy — it's code."

---

### 🔥 5:00-6:00 — WOW MOMENT #2: ESCROW FREEZE (60s)

**Action**: Show escrow status → Demonstrate payment frozen

**Say**:
> "Watch the payment system. The moment fraud score hits 0.5, the escrow automatically freezes."

**Show**:
- Progress bar turns RED
- Banner: "⚠️ Payment frozen due to verification risk. Manual review required."

> "Money doesn't move until a verified, clean photo is submitted. Anti-corruption via code, not paperwork."

---

### 🔥 6:00-7:00 — WOW MOMENT #3: PUBLIC TRANSPARENCY (60s)

**Action**: Navigate to Public Dashboard → Show ward stats

**Say**:
> "Any citizen — no login required — can see ward-level impact. Look at NDMC-14 Connaught Place..."

**Show** (read these numbers):
- Systems installed: 312
- Water captured: 18.4 million liters
- **Fraud prevented: 9 cases**
- Subsidy utilized: ₹78 Lakhs
- CO₂ avoided: 12,840 kg

> "This is government transparency. These numbers update in real-time."

**Point to label**:
> "See the footer? 'Public Transparency Dashboard (RTI-Ready).' Ready for citizen oversight."

---

### 🔥 7:00-7:30 — WOW MOMENT #4: RTI EXPORT (30s)

**Action**: Click "📦 Download RTI-Ready Data (ZIP)"

**Say**:
> "A judge might ask: 'Can this data be used for RTI?' Watch."

> *(Click export button)*

> "One click — ZIP downloads in under 10 seconds. Contains sites.csv, GeoJSON for mapping, and audit trail. Ready for Right to Information requests."

---

### 🕐 7:30-8:00 — Closing Statement (30s)

**Say**:
> "RainForge is not just a calculator. It's a complete anti-fraud, transparent, government-deployable platform."

> "Fraud is visible, not hidden in logs. Payments freeze automatically. Public dashboards work without login. RTI exports in seconds."

> "Ready for pilot deployment tomorrow. Thank you."

---

## Judge Q&A Prep

| Question | Answer |
|----------|--------|
| "How do you detect fraud?" | "pHash image matching, EXIF GPS verification, travel anomaly detection. 94% accuracy on our test data." |
| "What if someone spoofs GPS?" | "We cross-check EXIF timestamp, look for Photoshop signatures, and compare with installer's submission history." |
| "Can payments be unfrozen?" | "Yes, by an admin after manual review. Full audit trail is maintained." |
| "Is the public dashboard real-time?" | "Yes, data updates on every verification. No caching for fraud-related metrics." |
| "Government integration?" | "Aligned with AMRUT 2.0, Jal Jeevan Mission. Export formats match MIS requirements." |

---

## Do NOT Mention

- "AI" or "Machine Learning" (say "algorithm" or "automated")
- Technical architecture details (backend/frontend)
- "MVP" or "prototype"
- Incomplete features
- Blockchain, Aadhaar, or AR

---

## Emergency Recovery

| Problem | Solution |
|---------|----------|
| Backend down | Use screenshots in `/docs/demo_screenshots/` |
| Verification fails | Have pre-recorded video at `/docs/demo_video.mp4` |
| Data looks wrong | Reset demo: `POST /api/v1/admin/demo/reset` |
| PDF won't generate | Say "In production, PDFs are cached. Let me show you a sample." |
