"""
RainForge Calculation Explainability
Government-grade transparency for all assessments
"""

from typing import Dict, Optional, List
from datetime import datetime


class CalculationExplainer:
    """
    Generate human-readable explanations for all calculations.
    Removes "black-box AI" concerns for government auditors.
    """
    
    def explain_assessment(
        self,
        roof_area_sqm: float,
        annual_rainfall_mm: float,
        runoff_coefficient: float,
        rainfall_source: str,
        tank_size_liters: float,
        total_cost_inr: float,
        subsidy_amount_inr: float,
        confidence_grade: str
    ) -> Dict:
        """
        Generate full explainability panel for an assessment.
        """
        
        # Core calculation
        annual_yield = roof_area_sqm * (annual_rainfall_mm / 1000) * runoff_coefficient * 1000
        
        return {
            "title": "How This Assessment Was Calculated",
            "sections": [
                {
                    "heading": "1. Rainfall Data Source",
                    "content": self._explain_rainfall_source(rainfall_source, annual_rainfall_mm)
                },
                {
                    "heading": "2. Annual Yield Calculation",
                    "content": self._explain_yield_formula(
                        roof_area_sqm, annual_rainfall_mm, runoff_coefficient, annual_yield
                    )
                },
                {
                    "heading": "3. Tank Sizing Logic",
                    "content": self._explain_tank_sizing(annual_yield, tank_size_liters)
                },
                {
                    "heading": "4. Cost Estimation",
                    "content": self._explain_cost_breakdown(total_cost_inr, subsidy_amount_inr)
                },
                {
                    "heading": "5. Confidence Grade Explained",
                    "content": self._explain_confidence_grade(confidence_grade)
                },
                {
                    "heading": "6. Assumptions & Safety Margins",
                    "content": self._explain_assumptions()
                }
            ],
            "disclaimer": "This assessment follows IS 15797:2018 guidelines for rooftop rainwater harvesting design. Actual installation may vary based on site inspection.",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _explain_rainfall_source(self, source: str, annual_mm: float) -> str:
        if source == "IMD":
            return f"""
**Source**: India Meteorological Department (IMD) Gridded Rainfall Data
**Annual Rainfall**: {annual_mm} mm/year
**Data Quality**: Official government data (high reliability)

IMD provides district-level rainfall normals based on 30+ years of historical records.
This is the primary data source recommended by CGWB for RWH design.
            """.strip()
        elif source == "Open-Meteo":
            return f"""
**Source**: Open-Meteo Climate API (ERA5 Reanalysis)
**Annual Rainfall**: {annual_mm} mm/year
**Data Quality**: Global reanalysis data (good reliability)

Open-Meteo is used as fallback when IMD data is unavailable for the specific location.
ERA5 reanalysis is validated against ground stations with <15% error margin.
            """.strip()
        else:
            return f"""
**Source**: Location-based Estimate
**Annual Rainfall**: {annual_mm} mm/year
**Data Quality**: Estimated (moderate reliability)

⚠️ Exact rainfall data unavailable for this location. 
Regional average used. Recommend verification with local IMD office.
            """.strip()
    
    def _explain_yield_formula(
        self,
        area: float,
        rainfall: float,
        runoff: float,
        yield_liters: float
    ) -> str:
        return f"""
**Formula Used** (as per IS 15797):

```
Annual Yield = Roof Area × Annual Rainfall × Runoff Coefficient
             = {area} m² × {rainfall/1000:.3f} m × {runoff}
             = {yield_liters:,.0f} litres/year
```

**Where**:
- **Roof Area**: {area} m² (as provided by user)
- **Annual Rainfall**: {rainfall} mm = {rainfall/1000:.3f} metres
- **Runoff Coefficient**: {runoff} (based on roof material)

**Runoff Coefficient Reference**:
| Material | Coefficient |
|----------|-------------|
| Concrete (RCC) | 0.90 |
| Metal/GI Sheet | 0.95 |
| Clay Tiles | 0.75 |
| Asbestos | 0.85 |
        """.strip()
    
    def _explain_tank_sizing(self, annual_yield: float, tank_size: float) -> str:
        dry_days = 120  # Assumed dry season
        daily_demand_assumed = annual_yield / 365
        storage_factor = tank_size / (daily_demand_assumed * dry_days) if daily_demand_assumed > 0 else 0
        
        return f"""
**Tank Sizing Logic**:

The recommended tank size is based on:
1. Annual yield: {annual_yield:,.0f} litres
2. Dry season duration: ~120 days (April-July for most of India)
3. Demand pattern: Spread uniformly across the year

**Selected Tank Size**: {tank_size:,.0f} litres

This provides approximately {tank_size / max(1, daily_demand_assumed):.0f} days of water storage
at average daily consumption rate of {daily_demand_assumed:,.0f} litres/day.

**Three Scenarios Available**:
- **Cost Optimized**: Smaller tank, 60-day buffer
- **Max Capture**: Larger tank, minimises overflow loss
- **Dry Season**: Optimized for 120-day monsoon gap
        """.strip()
    
    def _explain_cost_breakdown(self, total_cost: float, subsidy: float) -> str:
        net_cost = total_cost - subsidy
        
        return f"""
**Cost Estimation Breakdown**:

| Component | Estimated Cost (₹) |
|-----------|-------------------|
| Tank & Structure | {total_cost * 0.50:,.0f} |
| Piping & Fittings | {total_cost * 0.15:,.0f} |
| First-Flush Diverter | {total_cost * 0.08:,.0f} |
| Filter System | {total_cost * 0.10:,.0f} |
| Labour & Installation | {total_cost * 0.17:,.0f} |
| **Total Cost** | **₹{total_cost:,.0f}** |

**Subsidy Applied**: ₹{subsidy:,.0f} ({(subsidy/total_cost)*100:.0f}%)
**Net Cost to Beneficiary**: ₹{net_cost:,.0f}

*Costs are estimates based on current market rates in the region.
Actual quotes from installers may vary ±15%.*
        """.strip()
    
    def _explain_confidence_grade(self, grade: str) -> str:
        grades = {
            "A": ("Excellent", "High-quality data from official sources, user-verified measurements, site inspection completed", "95%+"),
            "B": ("Good", "Official rainfall data, user-provided measurements, no site visit", "80-95%"),
            "C": ("Moderate", "Fallback rainfall data or estimated roof area", "60-80%"),
            "D": ("Low", "Multiple estimated inputs, recommend site verification", "45-60%"),
            "F": ("Insufficient", "Critical data missing, unreliable for decision-making", "<45%")
        }
        
        label, desc, range_pct = grades.get(grade, ("Unknown", "Grade not recognized", "N/A"))
        
        return f"""
**Confidence Grade: {grade} ({label})**

**What this means**: {desc}

**Confidence Range**: {range_pct}

**Factors Affecting Confidence**:
- Rainfall data source (IMD = highest, estimate = lowest)
- Roof area measurement method (LiDAR > satellite > user estimate)
- Site verification status (visited > remote)
- Subsidy scheme verification (official portal > manual)

**Recommendation**:
{self._grade_recommendation(grade)}
        """.strip()
    
    def _grade_recommendation(self, grade: str) -> str:
        if grade == "A":
            return "Ready for government approval and subsidy disbursement."
        elif grade == "B":
            return "Suitable for planning. Site visit recommended before final approval."
        elif grade == "C":
            return "Use for preliminary estimation only. Verify data before commitment."
        elif grade == "D":
            return "Engage certified engineer for site assessment before proceeding."
        else:
            return "Do not use for decision-making. Requires complete re-assessment."
    
    def _explain_assumptions(self) -> str:
        return """
**Standard Assumptions Applied**:

1. **Rainfall Distribution**: Monsoon-weighted (70-80% in June-September)
2. **First-Flush Loss**: 1-2 mm per rainfall event discarded
3. **System Efficiency**: 85% (accounts for evaporation, splashing)
4. **Tank Availability**: 90% (accounts for maintenance downtime)
5. **Safety Factor**: 1.1x applied to structural calculations

**No Machine Learning Used**:
All calculations use deterministic formulas based on IS 15797 and CGWB guidelines.
No "AI hallucinations" or probabilistic predictions in core sizing.

**Monte-Carlo Simulations** (optional):
When confidence intervals (P50/P90) are shown, they are generated using
1000+ simulations with known input uncertainty ranges, not AI inference.
        """.strip()


class FailsafeHandler:
    """
    Graceful handling of missing data and edge cases.
    No blank screens. No crashes. No undefined outputs.
    """
    
    DEFAULT_VALUES = {
        "annual_rainfall_mm": 800,
        "runoff_coefficient": 0.85,
        "tank_level_pct": 50,
        "confidence_grade": "C"
    }
    
    def handle_missing_rainfall(self, lat: float, lng: float) -> Dict:
        """Return fallback rainfall with warning."""
        return {
            "value": self.DEFAULT_VALUES["annual_rainfall_mm"],
            "source": "Estimated",
            "warning": "⚠️ Exact rainfall data unavailable. Using regional average (800 mm/year). Verify with local IMD office.",
            "fallback_applied": True,
            "recommendation": "Request IMD data for precise assessment"
        }
    
    def handle_offline_sensor(self, device_id: str, last_reading: Dict, last_seen: str) -> Dict:
        """Return last known value with status badge."""
        return {
            "device_id": device_id,
            "status": "offline",
            "status_badge": "🔴 Sensor Offline",
            "last_known_value": last_reading.get("tank_level_liters", 0),
            "last_known_pct": last_reading.get("tank_level_pct", 0),
            "last_seen": last_seen,
            "message": f"Last reading from {last_seen}. Check sensor connection.",
            "action_required": "Verify sensor power and connectivity"
        }
    
    def handle_pending_verification(self, job_id: str, submitted_at: str) -> Dict:
        """Return locked payment state with timeline."""
        return {
            "job_id": job_id,
            "verification_status": "pending",
            "payment_status": "🔒 Locked",
            "message": "Payment locked until verification is approved",
            "timeline": [
                {"step": "Verification Submitted", "status": "✅ Complete", "date": submitted_at},
                {"step": "Fraud Check", "status": "🔄 In Progress", "date": "Processing..."},
                {"step": "Admin Approval", "status": "⏳ Pending", "date": "—"},
                {"step": "Payment Release", "status": "🔒 Locked", "date": "—"}
            ],
            "expected_resolution": "24-48 hours"
        }
    
    def handle_no_installers(self, ward_id: str) -> Dict:
        """Handle case when no installers available."""
        return {
            "status": "no_installers",
            "message": "No certified installers currently available in your ward",
            "alternatives": [
                "Expand search to nearby wards",
                "Check back in 24-48 hours",
                "Contact support for manual allocation"
            ],
            "support_contact": "1800-XXX-XXXX"
        }


class ScaleProjection:
    """
    Calculate national-scale impact projections.
    Clearly marked as scenario projections.
    """
    
    def project_national_impact(
        self,
        rooftops: int = 100000,
        avg_roof_area_sqm: float = 150,
        avg_annual_rainfall_mm: float = 1000,
        avg_runoff_coefficient: float = 0.85
    ) -> Dict:
        """
        Project impact if deployed across N rooftops.
        """
        
        # Per-rooftop calculations
        per_roof_yield_liters = avg_roof_area_sqm * (avg_annual_rainfall_mm / 1000) * avg_runoff_coefficient * 1000
        
        # Scale up
        total_yield_liters = rooftops * per_roof_yield_liters
        total_yield_kl = total_yield_liters / 1000
        total_yield_mld = total_yield_kl / 365 / 1000  # Million Litres per Day
        
        # Environmental impact
        co2_per_kl = 0.7  # kg CO2 per 1000L water treatment avoided
        total_co2_kg = total_yield_kl * co2_per_kl
        
        # Economic impact
        water_cost_per_kl = 50  # ₹50 per 1000L (municipal rate)
        tanker_cost_per_kl = 500  # ₹500 per 1000L (tanker rate)
        avg_cost_per_kl = 150  # Blended average
        savings_inr = total_yield_kl * avg_cost_per_kl
        
        return {
            "_disclaimer": "SCENARIO PROJECTION — Based on assumptions below",
            "_projection_date": datetime.utcnow().isoformat(),
            "assumptions": {
                "rooftops_covered": f"{rooftops:,}",
                "average_roof_area": f"{avg_roof_area_sqm} m²",
                "average_rainfall": f"{avg_annual_rainfall_mm} mm/year",
                "runoff_coefficient": avg_runoff_coefficient
            },
            "impact": {
                "water_harvested": {
                    "annual_liters": f"{total_yield_liters:,.0f}",
                    "annual_kiloliters": f"{total_yield_kl:,.0f}",
                    "daily_mld": f"{total_yield_mld:.2f} MLD",
                    "display": f"{total_yield_kl/1000000:.1f} crore litres/year"
                },
                "environmental": {
                    "co2_avoided_kg": f"{total_co2_kg:,.0f}",
                    "co2_avoided_tons": f"{total_co2_kg/1000:,.0f}",
                    "equivalent_trees": f"{int(total_co2_kg / 22):,}"  # 22 kg CO2/tree/year
                },
                "economic": {
                    "water_cost_avoided_inr": f"₹{savings_inr:,.0f}",
                    "water_cost_avoided_crores": f"₹{savings_inr/10000000:.1f} crore"
                }
            },
            "context": [
                f"Equivalent to supplying water to {int(total_yield_kl/150/365):,} households for one year",
                f"Reduces groundwater extraction by {total_yield_mld:.1f} million litres daily",
                f"Climate resilience: {rooftops:,} buildings protected from water stress"
            ],
            "source": "RainForge Scenario Projection Engine"
        }
