"""
RainForge RPI (Performance Index) Calculator
Combines multiple metrics to create installer reliability score.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class RPIComponents:
    """Individual components of RPI score."""
    design_match_pct: float = 0.0      # How well as-built matches design
    yield_accuracy_pct: float = 0.0    # Predicted vs actual water yield
    timeliness_score: float = 0.0      # Job completion on time
    complaint_rate: float = 0.0        # Lower is better (inverted for scoring)
    maintenance_compliance: float = 0.0 # AMC visits completed on time
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "design_match_pct": round(self.design_match_pct, 1),
            "yield_accuracy_pct": round(self.yield_accuracy_pct, 1),
            "timeliness_score": round(self.timeliness_score, 1),
            "complaint_rate": round(self.complaint_rate, 2),
            "maintenance_compliance": round(self.maintenance_compliance, 1)
        }


@dataclass
class RPIWeights:
    """Configurable weights for RPI calculation."""
    design_match: float = 0.25
    yield_accuracy: float = 0.25
    timeliness: float = 0.20
    complaint_rate: float = 0.15
    maintenance: float = 0.15
    
    def normalize(self) -> 'RPIWeights':
        total = (self.design_match + self.yield_accuracy + self.timeliness + 
                 self.complaint_rate + self.maintenance)
        if total == 0:
            return RPIWeights()
        return RPIWeights(
            design_match=self.design_match / total,
            yield_accuracy=self.yield_accuracy / total,
            timeliness=self.timeliness / total,
            complaint_rate=self.complaint_rate / total,
            maintenance=self.maintenance / total
        )


class RPICalculator:
    """
    RainForge Performance Index Calculator.
    Computes installer reliability score from multiple metrics.
    """
    
    DEFAULT_WEIGHTS = RPIWeights()
    
    @classmethod
    def calculate(
        cls,
        components: RPIComponents,
        weights: Optional[RPIWeights] = None
    ) -> Dict:
        """
        Calculate RPI score from components.
        
        Returns:
            Dict with score, grade, and component breakdown
        """
        w = (weights or cls.DEFAULT_WEIGHTS).normalize()
        
        # Invert complaint rate (0 complaints = 100 score)
        complaint_score = max(0, 100 - (components.complaint_rate * 10))
        
        # Weighted calculation
        score = (
            components.design_match_pct * w.design_match +
            components.yield_accuracy_pct * w.yield_accuracy +
            components.timeliness_score * w.timeliness +
            complaint_score * w.complaint_rate +
            components.maintenance_compliance * w.maintenance
        )
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 90:
            grade = "A+"
            badge_color = "#10b981"  # Green
        elif score >= 80:
            grade = "A"
            badge_color = "#22c55e"
        elif score >= 70:
            grade = "B"
            badge_color = "#84cc16"
        elif score >= 60:
            grade = "C"
            badge_color = "#eab308"  # Yellow
        elif score >= 50:
            grade = "D"
            badge_color = "#f97316"  # Orange
        else:
            grade = "F"
            badge_color = "#ef4444"  # Red
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "badge_color": badge_color,
            "components": components.to_dict(),
            "weighted_breakdown": {
                "design_match": round(components.design_match_pct * w.design_match, 1),
                "yield_accuracy": round(components.yield_accuracy_pct * w.yield_accuracy, 1),
                "timeliness": round(components.timeliness_score * w.timeliness, 1),
                "complaint_rate": round(complaint_score * w.complaint_rate, 1),
                "maintenance": round(components.maintenance_compliance * w.maintenance, 1)
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def calculate_from_job_history(cls, jobs: List[Dict]) -> Dict:
        """
        Calculate RPI from a list of completed jobs.
        
        Args:
            jobs: List of job dicts with metrics
        """
        if not jobs:
            return cls.calculate(RPIComponents())
        
        # Aggregate metrics from jobs
        design_matches = []
        yield_accuracies = []
        on_time = 0
        complaints = 0
        maintenance_completed = 0
        maintenance_total = 0
        
        for job in jobs:
            if job.get("design_match_pct"):
                design_matches.append(job["design_match_pct"])
            if job.get("predicted_yield") and job.get("actual_yield"):
                accuracy = min(100, (job["actual_yield"] / job["predicted_yield"]) * 100)
                yield_accuracies.append(accuracy)
            if job.get("completed_on_time"):
                on_time += 1
            if job.get("has_complaint"):
                complaints += 1
            if job.get("maintenance_visits_required"):
                maintenance_total += job["maintenance_visits_required"]
                maintenance_completed += job.get("maintenance_visits_completed", 0)
        
        components = RPIComponents(
            design_match_pct=sum(design_matches) / len(design_matches) if design_matches else 80,
            yield_accuracy_pct=sum(yield_accuracies) / len(yield_accuracies) if yield_accuracies else 80,
            timeliness_score=(on_time / len(jobs)) * 100 if jobs else 80,
            complaint_rate=(complaints / len(jobs)) * 100 if jobs else 5,
            maintenance_compliance=(maintenance_completed / maintenance_total * 100) if maintenance_total > 0 else 90
        )
        
        return cls.calculate(components)
    
    @classmethod
    def get_improvement_suggestions(cls, rpi_result: Dict) -> List[str]:
        """Generate actionable suggestions to improve RPI."""
        suggestions = []
        breakdown = rpi_result.get("components", {})
        
        if breakdown.get("design_match_pct", 100) < 85:
            suggestions.append("Improve as-built documentation accuracy. Use standardized checklists.")
        
        if breakdown.get("yield_accuracy_pct", 100) < 85:
            suggestions.append("Calibrate yield predictions with local rainfall data.")
        
        if breakdown.get("timeliness_score", 100) < 80:
            suggestions.append("Set realistic timelines and track milestones closely.")
        
        if breakdown.get("complaint_rate", 0) > 5:
            suggestions.append("Review recent complaints and implement corrective actions.")
        
        if breakdown.get("maintenance_compliance", 100) < 90:
            suggestions.append("Ensure timely AMC visits. Set calendar reminders.")
        
        if not suggestions:
            suggestions.append("Maintain current standards. Consider advanced certification.")
        
        return suggestions


# ============== DEMO DATA ==============

def generate_demo_rpi(installer_id: int) -> Dict:
    """Generate realistic demo RPI data for an installer."""
    # Seed based on installer ID for consistency
    random.seed(installer_id * 42)
    
    components = RPIComponents(
        design_match_pct=random.uniform(70, 98),
        yield_accuracy_pct=random.uniform(75, 95),
        timeliness_score=random.uniform(65, 100),
        complaint_rate=random.uniform(0, 15),
        maintenance_compliance=random.uniform(70, 100)
    )
    
    result = RPICalculator.calculate(components)
    result["installer_id"] = installer_id
    result["suggestions"] = RPICalculator.get_improvement_suggestions(result)
    
    return result


def get_demo_rpi_for_all() -> List[Dict]:
    """Generate RPI data for all demo installers."""
    return [generate_demo_rpi(i) for i in range(1, 11)]
