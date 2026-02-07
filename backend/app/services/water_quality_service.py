"""
Water Quality Service
Water quality monitoring, sensor data, and test result management.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityReading:
    """Water quality sensor reading."""
    timestamp: datetime
    ph: Optional[float]
    tds_ppm: Optional[float]
    turbidity_ntu: Optional[float]
    temperature_c: Optional[float]
    overall_quality: str
    potable: bool


# Water quality standards (IS 10500:2012)
DRINKING_WATER_STANDARDS = {
    "ph": {"min": 6.5, "max": 8.5, "unit": "", "name": "pH"},
    "tds": {"min": 0, "max": 500, "unit": "ppm", "name": "Total Dissolved Solids"},
    "turbidity": {"min": 0, "max": 5, "unit": "NTU", "name": "Turbidity"},
    "hardness": {"min": 0, "max": 300, "unit": "ppm", "name": "Total Hardness"},
    "chloride": {"min": 0, "max": 250, "unit": "ppm", "name": "Chloride"},
    "nitrate": {"min": 0, "max": 45, "unit": "ppm", "name": "Nitrate"},
    "fluoride": {"min": 0, "max": 1.5, "unit": "ppm", "name": "Fluoride"},
    "iron": {"min": 0, "max": 0.3, "unit": "ppm", "name": "Iron"},
}


class WaterQualityService:
    """
    Service for water quality monitoring and management.
    
    Features:
    - Real-time sensor data ingestion (pH, TDS, Turbidity)
    - Lab test result uploads
    - Quality grading (A, B, C)
    - Treatment recommendations
    - Potability assessment
    - Historical trend analysis
    """
    
    def __init__(self):
        self.sensor_readings: Dict[int, List[Dict]] = {}
        self.lab_tests: Dict[int, List[Dict]] = {}
        self.alerts: Dict[int, List[Dict]] = {}
    
    # ==================== SENSOR DATA ====================
    
    def record_sensor_reading(
        self,
        project_id: int,
        device_id: str,
        ph: Optional[float] = None,
        tds_ppm: Optional[float] = None,
        turbidity_ntu: Optional[float] = None,
        temperature_c: Optional[float] = None,
        dissolved_oxygen_ppm: Optional[float] = None
    ) -> Dict[str, Any]:
        """Record a water quality sensor reading."""
        
        timestamp = datetime.utcnow()
        
        # Assess quality
        quality_grade, issues = self._assess_quality(ph, tds_ppm, turbidity_ntu)
        potable = quality_grade == "A" and not issues
        
        reading = {
            "reading_id": f"QR-{project_id}-{timestamp.strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "device_id": device_id,
            "timestamp": timestamp.isoformat(),
            
            # Readings
            "ph": ph,
            "tds_ppm": tds_ppm,
            "turbidity_ntu": turbidity_ntu,
            "temperature_c": temperature_c,
            "dissolved_oxygen_ppm": dissolved_oxygen_ppm,
            
            # Assessment
            "quality_grade": quality_grade,
            "issues": issues,
            "potable": potable,
            "suitable_uses": self._get_suitable_uses(quality_grade)
        }
        
        if project_id not in self.sensor_readings:
            self.sensor_readings[project_id] = []
        
        self.sensor_readings[project_id].append(reading)
        
        # Generate alerts if needed
        if issues:
            self._generate_quality_alert(project_id, reading, issues)
        
        logger.info(f"Recorded quality reading for project {project_id}: Grade {quality_grade}")
        
        return reading
    
    def _assess_quality(
        self,
        ph: Optional[float],
        tds_ppm: Optional[float],
        turbidity_ntu: Optional[float]
    ) -> tuple:
        """Assess water quality based on readings."""
        
        issues = []
        score = 100
        
        # pH assessment
        if ph is not None:
            if ph < 6.5:
                issues.append(f"pH too low ({ph}): Water is acidic")
                score -= 20
            elif ph > 8.5:
                issues.append(f"pH too high ({ph}): Water is alkaline")
                score -= 20
        
        # TDS assessment
        if tds_ppm is not None:
            if tds_ppm > 500:
                issues.append(f"TDS high ({tds_ppm} ppm): Exceeds drinking water limit")
                score -= 30
            elif tds_ppm > 300:
                issues.append(f"TDS elevated ({tds_ppm} ppm)")
                score -= 10
        
        # Turbidity assessment
        if turbidity_ntu is not None:
            if turbidity_ntu > 5:
                issues.append(f"High turbidity ({turbidity_ntu} NTU): Needs filtration")
                score -= 30
            elif turbidity_ntu > 1:
                issues.append(f"Elevated turbidity ({turbidity_ntu} NTU)")
                score -= 10
        
        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        else:
            grade = "C"
        
        return grade, issues
    
    def _get_suitable_uses(self, grade: str) -> List[str]:
        """Get suitable uses based on quality grade."""
        uses = {
            "A": [
                "Drinking (with basic treatment)",
                "Cooking",
                "Bathing",
                "Washing",
                "Gardening",
                "Toilet flushing",
                "Groundwater recharge"
            ],
            "B": [
                "Bathing",
                "Washing",
                "Gardening",
                "Toilet flushing",
                "Groundwater recharge"
            ],
            "C": [
                "Gardening only",
                "Groundwater recharge"
            ]
        }
        return uses.get(grade, ["Groundwater recharge only"])
    
    def _generate_quality_alert(
        self,
        project_id: int,
        reading: Dict,
        issues: List[str]
    ):
        """Generate alert for quality issues."""
        
        alert = {
            "alert_id": f"QA-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "alert_type": "quality_issue",
            "severity": "warning" if reading["quality_grade"] == "B" else "critical",
            "message": f"Water quality issues detected: {'; '.join(issues)}",
            "reading_id": reading["reading_id"],
            "triggered_at": datetime.utcnow().isoformat(),
            "acknowledged": False
        }
        
        if project_id not in self.alerts:
            self.alerts[project_id] = []
        
        self.alerts[project_id].append(alert)
        
        logger.warning(f"Quality alert for project {project_id}: {issues}")
    
    # ==================== LAB TEST RESULTS ====================
    
    def upload_lab_test(
        self,
        project_id: int,
        test_date: date,
        lab_name: str,
        ph: float,
        tds_ppm: float,
        turbidity_ntu: float,
        hardness_ppm: Optional[float] = None,
        chloride_ppm: Optional[float] = None,
        nitrate_ppm: Optional[float] = None,
        fluoride_ppm: Optional[float] = None,
        iron_ppm: Optional[float] = None,
        coliform_present: Optional[bool] = None,
        e_coli_present: Optional[bool] = None,
        report_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload lab test results."""
        
        # Validate against standards
        validation_results, overall_pass = self._validate_test_results({
            "ph": ph,
            "tds": tds_ppm,
            "turbidity": turbidity_ntu,
            "hardness": hardness_ppm,
            "chloride": chloride_ppm,
            "nitrate": nitrate_ppm,
            "fluoride": fluoride_ppm,
            "iron": iron_ppm
        })
        
        # Check biological contamination
        biological_safe = True
        if coliform_present or e_coli_present:
            biological_safe = False
            overall_pass = False
        
        # Generate treatment recommendations
        treatments = self._get_treatment_recommendations(
            validation_results, coliform_present, e_coli_present
        )
        
        test_result = {
            "test_id": f"LAB-{project_id}-{test_date.isoformat()}",
            "project_id": project_id,
            "test_date": test_date.isoformat(),
            "lab_name": lab_name,
            "uploaded_at": datetime.utcnow().isoformat(),
            
            # Results
            "results": {
                "ph": {"value": ph, **validation_results.get("ph", {})},
                "tds_ppm": {"value": tds_ppm, **validation_results.get("tds", {})},
                "turbidity_ntu": {"value": turbidity_ntu, **validation_results.get("turbidity", {})},
                "hardness_ppm": {"value": hardness_ppm, **validation_results.get("hardness", {})} if hardness_ppm else None,
                "chloride_ppm": {"value": chloride_ppm, **validation_results.get("chloride", {})} if chloride_ppm else None,
                "nitrate_ppm": {"value": nitrate_ppm, **validation_results.get("nitrate", {})} if nitrate_ppm else None,
                "fluoride_ppm": {"value": fluoride_ppm, **validation_results.get("fluoride", {})} if fluoride_ppm else None,
                "iron_ppm": {"value": iron_ppm, **validation_results.get("iron", {})} if iron_ppm else None,
                "coliform_present": coliform_present,
                "e_coli_present": e_coli_present
            },
            
            # Assessment
            "suitable_for_drinking": overall_pass and biological_safe,
            "biological_safe": biological_safe,
            "treatment_required": treatments,
            "quality_grade": "A" if overall_pass and biological_safe else "B" if overall_pass else "C",
            
            # Report
            "report_url": report_url
        }
        
        if project_id not in self.lab_tests:
            self.lab_tests[project_id] = []
        
        self.lab_tests[project_id].append(test_result)
        
        logger.info(f"Lab test uploaded for project {project_id}: {'PASS' if overall_pass else 'FAIL'}")
        
        return test_result
    
    def _validate_test_results(self, results: Dict) -> tuple:
        """Validate test results against standards."""
        
        validation = {}
        all_pass = True
        
        for param, value in results.items():
            if value is None:
                continue
            
            standard = DRINKING_WATER_STANDARDS.get(param)
            if not standard:
                continue
            
            passed = standard["min"] <= value <= standard["max"]
            if not passed:
                all_pass = False
            
            validation[param] = {
                "standard_min": standard["min"],
                "standard_max": standard["max"],
                "unit": standard["unit"],
                "passed": passed,
                "status": "✓ Pass" if passed else "✗ Fail"
            }
        
        return validation, all_pass
    
    def _get_treatment_recommendations(
        self,
        validation_results: Dict,
        coliform: Optional[bool],
        e_coli: Optional[bool]
    ) -> List[str]:
        """Get treatment recommendations based on test results."""
        
        treatments = []
        
        # Check each parameter
        for param, result in validation_results.items():
            if not result.get("passed", True):
                treatments.extend(self._get_param_treatment(param))
        
        # Biological contamination
        if coliform or e_coli:
            treatments.extend([
                "UV disinfection system required",
                "Chlorination (0.5 mg/L free chlorine)",
                "Boiling before drinking",
                "Investigate contamination source"
            ])
        
        return list(set(treatments))  # Remove duplicates
    
    def _get_param_treatment(self, param: str) -> List[str]:
        """Get treatment for specific parameter failure."""
        
        treatments = {
            "ph": ["pH correction using neutralizing filter"],
            "tds": ["RO (Reverse Osmosis) filtration"],
            "turbidity": ["Sand filtration", "Settling tank"],
            "hardness": ["Water softener", "RO filtration"],
            "chloride": ["RO filtration"],
            "nitrate": ["RO filtration", "Ion exchange"],
            "fluoride": ["Activated alumina filter", "RO filtration"],
            "iron": ["Iron removal filter", "Aeration + filtration"]
        }
        
        return treatments.get(param, [])
    
    # ==================== QUALITY HISTORY ====================
    
    def get_quality_history(
        self,
        project_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get quality history for a project."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get sensor readings
        readings = [
            r for r in self.sensor_readings.get(project_id, [])
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]
        
        # Get lab tests
        lab_tests = self.lab_tests.get(project_id, [])
        
        # Calculate trends
        if readings:
            avg_ph = sum(r["ph"] for r in readings if r["ph"]) / len([r for r in readings if r["ph"]]) if any(r["ph"] for r in readings) else None
            avg_tds = sum(r["tds_ppm"] for r in readings if r["tds_ppm"]) / len([r for r in readings if r["tds_ppm"]]) if any(r["tds_ppm"] for r in readings) else None
            avg_turbidity = sum(r["turbidity_ntu"] for r in readings if r["turbidity_ntu"]) / len([r for r in readings if r["turbidity_ntu"]]) if any(r["turbidity_ntu"] for r in readings) else None
            
            grade_counts = {"A": 0, "B": 0, "C": 0}
            for r in readings:
                grade_counts[r["quality_grade"]] = grade_counts.get(r["quality_grade"], 0) + 1
            
            most_common_grade = max(grade_counts, key=grade_counts.get)
        else:
            avg_ph = avg_tds = avg_turbidity = None
            most_common_grade = "Unknown"
        
        return {
            "project_id": project_id,
            "period_days": days,
            "total_readings": len(readings),
            "total_lab_tests": len(lab_tests),
            
            # Averages
            "average_ph": round(avg_ph, 2) if avg_ph else None,
            "average_tds_ppm": round(avg_tds, 1) if avg_tds else None,
            "average_turbidity_ntu": round(avg_turbidity, 2) if avg_turbidity else None,
            
            # Trend
            "most_common_grade": most_common_grade,
            "potable_readings_percent": round(
                sum(1 for r in readings if r["potable"]) / len(readings) * 100, 1
            ) if readings else 0,
            
            # Recent readings
            "recent_readings": readings[-10:] if readings else [],
            
            # Lab tests
            "lab_tests": lab_tests
        }
    
    def get_quality_alerts(
        self,
        project_id: int,
        unacknowledged_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get quality alerts for a project."""
        
        alerts = self.alerts.get(project_id, [])
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a["acknowledged"]]
        
        return sorted(alerts, key=lambda x: x["triggered_at"], reverse=True)
    
    def acknowledge_alert(self, project_id: int, alert_id: str) -> bool:
        """Acknowledge a quality alert."""
        
        alerts = self.alerts.get(project_id, [])
        
        for alert in alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                return True
        
        return False


# Singleton instance
_quality_service: Optional[WaterQualityService] = None


def get_water_quality_service() -> WaterQualityService:
    """Get or create water quality service instance."""
    global _quality_service
    if _quality_service is None:
        _quality_service = WaterQualityService()
    return _quality_service
