# RainForge Demo Script
**For Hackathon Judges - 3 Minute Walkthrough**

---

## Quick Start

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend
npm install
npm run dev
```

Then open: http://localhost:5173

---

## Demo Flow (3 minutes)

### Scene 1: Public Dashboard (30s)
**URL:** http://localhost:5173/public

1. Show city-level water capture stats
2. Point out ward-wise breakdown chart
3. Click "Export CSV" to download data
4. Highlight: "This is citizen transparency"

### Scene 2: Smart Allocation (45s)
**URL:** http://localhost:5173/marketplace

1. Show 3 allocation modes: User/Gov/Equitable
2. Select "Gov Optimized" 
3. Click "Run Allocation for Demo Job #116"
4. Show:
   - Recommended installer with score
   - Score breakdown (RPI, Distance, Capacity...)
   - Alternatives ranked below
5. Click "Tune Weights" → adjust RPI slider → re-run

### Scene 3: Competitive Bidding (45s)
Tab: "Competitive Bidding"

1. Click "Demo Bids" to load sample bids
2. Show bid ranking table with:
   - Price vs estimated
   - Timeline
   - Warranty
   - Composite score
3. Click "Award Bid" on top-ranked installer
4. Show confirmation

### Scene 4: Escrow & Payments (45s)
Tab: "Escrow & Payments"

1. Click "Create Escrow Payment"
2. Show 4 milestones:
   - Design Approval (20%)
   - Installation Complete (40%)
   - Verification Passed (30%)
   - Post-Performance (10%)
3. Click "Mark Complete" on first milestone
4. Click "Verify (Admin)"
5. Click "Release Funds" - show amount moving from escrow

### Scene 5: Verification & Fraud (30s)
**URL:** http://localhost:5173/verification

1. Show verification upload form
2. Point out geo-tag validation
3. Mention: "Fraud detection checks photo reuse, geo mismatch, timestamp anomalies"

### Closing (15s)
- Mention: "All backed by PostgreSQL-ready schema"
- Show API docs: http://localhost:8000/docs
- "Ready for 10,000 household pilot"

---

## Key Features to Highlight

| Feature | Demo Point |
|---------|-----------|
| 3 Allocation Modes | Gov can optimize for RPI or equitable distribution |
| RPI Scoring | Installer reliability built from real metrics |
| Competitive Bidding | Transparent, scorable bids |
| Escrow Payments | Milestone-based, fraud-resistant |
| Fraud Detection | Photo reuse, geo mismatch alerts |
| Public Dashboard | Citizen transparency with export |

---

## API Endpoints to Show

```
GET  /api/v1/marketplace/installers      # List with RPI
POST /api/v1/marketplace/allocate        # Smart allocation
POST /api/v1/marketplace/bids            # Submit bid
POST /api/v1/payments                     # Create escrow
GET  /api/v1/public/city/stats           # Transparency data
```

---

## Fallback: If Backend Fails

All frontend components include mock data. The demo will work without backend by using:
- Demo Bids button
- Mock allocation results
- Simulated payment flow

---

*RainForge Government Edition v3.0*
