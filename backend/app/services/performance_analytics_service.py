"""
Performance Analytics Service
Track actual vs projected performance, neighbor comparisons, and maintenance reminders.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging
import random

logger = logging.getLogger(__name__)


@dataclass
class MonthlyPerformance:
    """Monthly performance data."""
    month: str
    year: int
    actual_rainfall_mm: float
    actual_collection_liters: float
    actual_usage_liters: float
    projected_collection_liters: float
    avg_tank_level_percent: float
    days_data_available: int


@dataclass
class MaintenanceTask:
    """Maintenance task."""
    task_id: str
    task_name: str
    description: str
    frequency: str
    last_completed: Optional[date]
    next_due: date
    priority: str
    estimated_cost: float


class PerformanceAnalyticsService:
    """
    Service for tracking RWH system performance.
    
    Features:
    - Actual vs projected collection tracking
    - Annual performance reports
    - Neighbor/area comparison (gamification)
    - Leaderboards
    - Maintenance reminders
    - Pre-monsoon checklists
    """
    
    # Monthly rainfall distribution (India average)
    MONTHLY_DISTRIBUTION = {
        "January": 0.02, "February": 0.02, "March": 0.03, "April": 0.04,
        "May": 0.05, "June": 0.15, "July": 0.25, "August": 0.22,
        "September": 0.14, "October": 0.05, "November": 0.02, "December": 0.01
    }
    
    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Maintenance tasks
    DEFAULT_MAINTENANCE_TASKS = [
        {
            "task_name": "Clean Gutters",
            "description": "Remove leaves, debris, and sediment from gutters",
            "frequency": "quarterly",
            "priority": "high",
            "estimated_cost": 0
        },
        {
            "task_name": "Clean Filter",
            "description": "Clean or replace rainwater filter",
            "frequency": "monthly",
            "priority": "high",
            "estimated_cost": 200
        },
        {
            "task_name": "Empty First Flush",
            "description": "Empty and clean first flush diverter",
            "frequency": "after_rain",
            "priority": "medium",
            "estimated_cost": 0
        },
        {
            "task_name": "Inspect Tank",
            "description": "Visual inspection of tank for cracks or leaks",
            "frequency": "quarterly",
            "priority": "medium",
            "estimated_cost": 0
        },
        {
            "task_name": "Clean Tank",
            "description": "Complete tank cleaning and disinfection",
            "frequency": "annual",
            "priority": "high",
            "estimated_cost": 1500
        },
        {
            "task_name": "Check Pipes",
            "description": "Inspect downpipes and connections for leaks",
            "frequency": "quarterly",
            "priority": "medium",
            "estimated_cost": 0
        },
        {
            "task_name": "Pre-Monsoon Check",
            "description": "Complete system check before monsoon season",
            "frequency": "annual",
            "priority": "critical",
            "estimated_cost": 500
        }
    ]
    
    def __init__(self):
        self.performance_data: Dict[int, List[MonthlyPerformance]] = {}
        self.maintenance_schedules: Dict[int, List[Dict]] = {}
        self.project_data: Dict[int, Dict] = {}
    
    # ==================== PERFORMANCE TRACKING ====================
    
    def record_monthly_performance(
        self,
        project_id: int,
        month: str,
        year: int,
        actual_rainfall_mm: float,
        actual_collection_liters: float,
        actual_usage_liters: float,
        avg_tank_level_percent: float,
        days_data_available: int = 30
    ) -> MonthlyPerformance:
        """Record monthly performance data."""
        
        # Get projected collection
        projected = self._get_projected_collection(project_id, month, year)
        
        performance = MonthlyPerformance(
            month=month,
            year=year,
            actual_rainfall_mm=actual_rainfall_mm,
            actual_collection_liters=actual_collection_liters,
            actual_usage_liters=actual_usage_liters,
            projected_collection_liters=projected,
            avg_tank_level_percent=avg_tank_level_percent,
            days_data_available=days_data_available
        )
        
        if project_id not in self.performance_data:
            self.performance_data[project_id] = []
        
        # Remove existing entry for same month/year if exists
        self.performance_data[project_id] = [
            p for p in self.performance_data[project_id]
            if not (p.month == month and p.year == year)
        ]
        
        self.performance_data[project_id].append(performance)
        
        logger.info(f"Recorded performance for project {project_id}: {month} {year}")
        
        return performance
    
    def _get_projected_collection(
        self,
        project_id: int,
        month: str,
        year: int
    ) -> float:
        """Get projected collection for a month."""
        # This would normally come from the original assessment
        # Using placeholder calculation
        project = self.project_data.get(project_id, {})
        annual_projected = project.get("annual_projected_liters", 100000)
        
        monthly_percent = self.MONTHLY_DISTRIBUTION.get(month, 0.08)
        return annual_projected * monthly_percent
    
    def get_annual_performance_report(
        self,
        project_id: int,
        year: int
    ) -> Dict[str, Any]:
        """Generate annual performance report."""
        
        project = self.project_data.get(project_id, {})
        monthly_data = [
            p for p in self.performance_data.get(project_id, [])
            if p.year == year
        ]
        
        if not monthly_data:
            # Generate demo data
            monthly_data = self._generate_demo_monthly_data(project_id, year)
        
        # Calculate totals
        total_rainfall = sum(m.actual_rainfall_mm for m in monthly_data)
        total_collection = sum(m.actual_collection_liters for m in monthly_data)
        total_usage = sum(m.actual_usage_liters for m in monthly_data)
        total_projected = sum(m.projected_collection_liters for m in monthly_data)
        
        # Overflow (collection - usage when tank full)
        total_overflow = max(0, total_collection - total_usage - project.get("tank_capacity", 10000))
        
        # Savings calculation
        water_rate = project.get("water_rate_per_liter", 0.02)  # ₹0.02/liter
        water_bill_savings = total_collection * water_rate
        tanker_cost_saved = project.get("monthly_tanker_expense", 0) * 12 * 0.6  # 60% reduction
        total_savings = water_bill_savings + tanker_cost_saved
        
        # Environmental impact
        carbon_offset = (total_collection / 1000) * 0.5  # 0.5 kg CO2 per 1000L
        groundwater_recharged = total_collection * 0.3 if project.get("has_recharge") else 0
        
        # Scores
        efficiency_percent = (total_collection / total_projected * 100) if total_projected > 0 else 0
        performance_score = min(100, int(efficiency_percent))
        reliability_score = self._calculate_reliability_score(monthly_data)
        
        # Maintenance status
        maintenance = self.maintenance_schedules.get(project_id, [])
        maintenance_completed = sum(1 for m in maintenance if m.get("last_completed"))
        maintenance_pending = len(maintenance) - maintenance_completed
        
        report = {
            "project_id": project_id,
            "year": year,
            "generated_at": datetime.utcnow().isoformat(),
            
            # Summary
            "total_rainfall_mm": round(total_rainfall, 1),
            "total_collection_liters": round(total_collection),
            "total_usage_liters": round(total_usage),
            "total_overflow_liters": round(total_overflow),
            
            # Comparison
            "projected_collection_liters": round(total_projected),
            "actual_vs_projected_percent": round(efficiency_percent, 1),
            
            # Savings
            "water_bill_savings_inr": round(water_bill_savings),
            "tanker_savings_inr": round(tanker_cost_saved),
            "total_savings_inr": round(total_savings),
            
            # Environmental
            "carbon_offset_kg": round(carbon_offset, 1),
            "groundwater_recharged_liters": round(groundwater_recharged),
            
            # Monthly Breakdown
            "monthly_data": [
                {
                    "month": m.month,
                    "actual_rainfall_mm": m.actual_rainfall_mm,
                    "actual_collection_liters": m.actual_collection_liters,
                    "projected_collection_liters": m.projected_collection_liters,
                    "efficiency_percent": round(
                        m.actual_collection_liters / m.projected_collection_liters * 100
                        if m.projected_collection_liters > 0 else 0, 1
                    ),
                    "avg_tank_level_percent": m.avg_tank_level_percent
                }
                for m in monthly_data
            ],
            
            # Maintenance
            "maintenance_completed": maintenance_completed,
            "maintenance_pending": maintenance_pending,
            
            # Scores
            "performance_score": performance_score,
            "reliability_score": reliability_score
        }
        
        return report
    
    def _generate_demo_monthly_data(
        self,
        project_id: int,
        year: int
    ) -> List[MonthlyPerformance]:
        """Generate demo monthly data for testing."""
        data = []
        
        project = self.project_data.get(project_id, {})
        annual_projected = project.get("annual_projected_liters", 100000)
        annual_rainfall = project.get("annual_rainfall_mm", 1000)
        
        for month in self.MONTH_NAMES:
            monthly_percent = self.MONTHLY_DISTRIBUTION.get(month, 0.08)
            projected = annual_projected * monthly_percent
            
            # Add some variance
            variance = random.uniform(0.8, 1.2)
            actual = projected * variance
            
            data.append(MonthlyPerformance(
                month=month,
                year=year,
                actual_rainfall_mm=annual_rainfall * monthly_percent * random.uniform(0.9, 1.1),
                actual_collection_liters=actual,
                actual_usage_liters=projected * 0.8,
                projected_collection_liters=projected,
                avg_tank_level_percent=random.uniform(30, 80),
                days_data_available=random.randint(25, 30)
            ))
        
        return data
    
    def _calculate_reliability_score(self, monthly_data: List[MonthlyPerformance]) -> int:
        """Calculate system reliability score."""
        if not monthly_data:
            return 0
        
        # Based on data availability and consistency
        avg_data_days = sum(m.days_data_available for m in monthly_data) / len(monthly_data)
        data_score = min(50, int(avg_data_days / 30 * 50))
        
        # Based on efficiency consistency
        efficiencies = [
            m.actual_collection_liters / m.projected_collection_liters
            if m.projected_collection_liters > 0 else 0
            for m in monthly_data
        ]
        avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
        efficiency_score = min(50, int(avg_efficiency * 50))
        
        return data_score + efficiency_score
    
    # ==================== NEIGHBOR COMPARISON ====================
    
    def get_neighbor_comparison(
        self,
        project_id: int,
        city: str,
        year: int = None
    ) -> Dict[str, Any]:
        """Compare performance with neighbors in same area."""
        
        year = year or datetime.now().year
        
        # Get this project's performance
        my_report = self.get_annual_performance_report(project_id, year)
        
        # Simulate area statistics (in production, query from database)
        area_projects = random.randint(50, 200)
        area_avg_collection = my_report["total_collection_liters"] * random.uniform(0.8, 1.0)
        area_avg_efficiency = my_report["actual_vs_projected_percent"] * random.uniform(0.85, 0.95)
        area_avg_savings = my_report["total_savings_inr"] * random.uniform(0.75, 0.9)
        
        # Calculate rank
        my_rank = random.randint(1, max(1, int(area_projects * 0.3)))  # Top 30%
        percentile = 100 - int(my_rank / area_projects * 100)
        
        # Top performers (demo)
        top_performers = [
            {
                "rank": i + 1,
                "area": f"Sector {random.randint(1, 50)}",
                "collection_liters": int(my_report["total_collection_liters"] * random.uniform(1.1, 1.5)),
                "efficiency_percent": round(random.uniform(90, 100), 1)
            }
            for i in range(5)
        ]
        
        return {
            "project_id": project_id,
            "city": city,
            "year": year,
            
            # Your Stats
            "your_collection_liters": my_report["total_collection_liters"],
            "your_efficiency_percent": my_report["actual_vs_projected_percent"],
            "your_savings_inr": my_report["total_savings_inr"],
            
            # Area Stats
            "area_average_collection": round(area_avg_collection),
            "area_average_efficiency": round(area_avg_efficiency, 1),
            "area_average_savings": round(area_avg_savings),
            
            # Ranking
            "area_rank": my_rank,
            "total_in_area": area_projects,
            "percentile": percentile,
            
            # Comparison
            "vs_average_collection_percent": round(
                (my_report["total_collection_liters"] / area_avg_collection - 1) * 100, 1
            ) if area_avg_collection > 0 else 0,
            "vs_average_savings_percent": round(
                (my_report["total_savings_inr"] / area_avg_savings - 1) * 100, 1
            ) if area_avg_savings > 0 else 0,
            
            # Leaderboard
            "top_performers": top_performers,
            
            # Message
            "message": self._get_comparison_message(percentile)
        }
    
    def _get_comparison_message(self, percentile: int) -> str:
        """Get motivational message based on percentile."""
        if percentile >= 90:
            return "🏆 Outstanding! You're in the top 10% of water harvesters in your area!"
        elif percentile >= 75:
            return "⭐ Excellent! You're outperforming 75% of your neighbors!"
        elif percentile >= 50:
            return "👍 Good job! You're above average in your area."
        elif percentile >= 25:
            return "💪 Keep improving! Check maintenance tips to boost collection."
        else:
            return "📈 Room for improvement. Schedule a system check."
    
    def get_leaderboard(
        self,
        city: str,
        state: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get area leaderboard."""
        
        # Demo leaderboard data
        leaderboard = []
        
        for i in range(limit):
            leaderboard.append({
                "rank": i + 1,
                "project_id": 1000 + i,
                "area": f"Sector {random.randint(1, 50)}, {city}",
                "annual_collection_liters": int(random.uniform(100000, 500000)),
                "efficiency_percent": round(random.uniform(75, 100), 1),
                "carbon_offset_kg": round(random.uniform(50, 250), 1),
                "badge": "🏆" if i < 3 else "⭐" if i < 5 else ""
            })
        
        return leaderboard
    
    # ==================== MAINTENANCE REMINDERS ====================
    
    def initialize_maintenance_schedule(
        self,
        project_id: int,
        installation_date: date,
        has_recharge: bool = False
    ) -> List[Dict[str, Any]]:
        """Initialize maintenance schedule for a project."""
        
        schedule = []
        today = date.today()
        
        for task in self.DEFAULT_MAINTENANCE_TASKS:
            next_due = self._calculate_next_due(
                task["frequency"],
                installation_date,
                today
            )
            
            schedule.append({
                "task_id": f"{project_id}-{task['task_name'].replace(' ', '_').lower()}",
                "task_name": task["task_name"],
                "description": task["description"],
                "frequency": task["frequency"],
                "priority": task["priority"],
                "estimated_cost": task["estimated_cost"],
                "last_completed": None,
                "next_due": next_due.isoformat(),
                "is_overdue": next_due < today,
                "days_until_due": (next_due - today).days
            })
        
        # Add recharge pit cleaning if applicable
        if has_recharge:
            next_pre_monsoon = date(today.year, 5, 1)  # May 1
            if next_pre_monsoon < today:
                next_pre_monsoon = date(today.year + 1, 5, 1)
            
            schedule.append({
                "task_id": f"{project_id}-clean_recharge_pit",
                "task_name": "Clean Recharge Pit",
                "description": "Clean recharge pit and refill filter media",
                "frequency": "annual",
                "priority": "high",
                "estimated_cost": 2000,
                "last_completed": None,
                "next_due": next_pre_monsoon.isoformat(),
                "is_overdue": False,
                "days_until_due": (next_pre_monsoon - today).days
            })
        
        self.maintenance_schedules[project_id] = schedule
        
        return schedule
    
    def _calculate_next_due(
        self,
        frequency: str,
        installation_date: date,
        today: date
    ) -> date:
        """Calculate next due date for a maintenance task."""
        
        if frequency == "monthly":
            next_due = today.replace(day=1) + timedelta(days=32)
            return next_due.replace(day=1)
        
        elif frequency == "quarterly":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            next_quarter = quarter_start_month + 3
            year = today.year
            if next_quarter > 12:
                next_quarter = 1
                year += 1
            return date(year, next_quarter, 1)
        
        elif frequency == "annual":
            next_year = date(today.year + 1, installation_date.month, 1)
            if next_year.month < today.month:
                next_year = date(today.year, installation_date.month, 1)
            return next_year
        
        elif frequency == "after_rain":
            # Check after each significant rain
            return today + timedelta(days=7)
        
        else:
            return today + timedelta(days=30)
    
    def complete_maintenance_task(
        self,
        project_id: int,
        task_id: str,
        completed_date: date = None,
        notes: str = "",
        cost_incurred: float = 0
    ) -> Dict[str, Any]:
        """Mark a maintenance task as completed."""
        
        schedule = self.maintenance_schedules.get(project_id, [])
        
        for task in schedule:
            if task["task_id"] == task_id:
                completed_date = completed_date or date.today()
                task["last_completed"] = completed_date.isoformat()
                task["completion_notes"] = notes
                task["actual_cost"] = cost_incurred
                
                # Calculate next due
                next_due = self._calculate_next_due(
                    task["frequency"],
                    completed_date,
                    date.today()
                )
                task["next_due"] = next_due.isoformat()
                task["is_overdue"] = False
                task["days_until_due"] = (next_due - date.today()).days
                
                logger.info(f"Completed maintenance task {task_id} for project {project_id}")
                return task
        
        raise ValueError(f"Task not found: {task_id}")
    
    def get_maintenance_reminders(
        self,
        project_id: int,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming maintenance reminders."""
        
        schedule = self.maintenance_schedules.get(project_id, [])
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        
        reminders = []
        
        for task in schedule:
            due_date = date.fromisoformat(task["next_due"])
            
            if due_date <= cutoff:
                reminders.append({
                    "task_id": task["task_id"],
                    "task_name": task["task_name"],
                    "description": task["description"],
                    "next_due": task["next_due"],
                    "is_overdue": due_date < today,
                    "days_until_due": (due_date - today).days,
                    "priority": task["priority"],
                    "estimated_cost": task["estimated_cost"]
                })
        
        # Sort by due date
        reminders.sort(key=lambda x: x["next_due"])
        
        return reminders
    
    def get_premonsoon_checklist(self, project_id: int) -> Dict[str, Any]:
        """Get pre-monsoon preparation checklist."""
        
        checklist = [
            {
                "item": "Clean all gutters and downpipes",
                "description": "Remove leaves, debris, and bird nests",
                "priority": "critical",
                "estimated_time_mins": 60
            },
            {
                "item": "Inspect and clean filters",
                "description": "Replace filter media if needed",
                "priority": "critical",
                "estimated_time_mins": 30
            },
            {
                "item": "Check first flush diverter",
                "description": "Ensure ball valve is functioning properly",
                "priority": "high",
                "estimated_time_mins": 15
            },
            {
                "item": "Inspect storage tank",
                "description": "Check for cracks, clean interior",
                "priority": "high",
                "estimated_time_mins": 120
            },
            {
                "item": "Test all pipe connections",
                "description": "Check for leaks and blockages",
                "priority": "medium",
                "estimated_time_mins": 45
            },
            {
                "item": "Clean recharge pit (if applicable)",
                "description": "Remove sediment and replace filter layers",
                "priority": "high",
                "estimated_time_mins": 180
            },
            {
                "item": "Check overflow pipe",
                "description": "Ensure clear path for excess water",
                "priority": "medium",
                "estimated_time_mins": 15
            },
            {
                "item": "Verify pump operation",
                "description": "Test submersible pump if installed",
                "priority": "medium",
                "estimated_time_mins": 15
            },
            {
                "item": "Update IoT sensors",
                "description": "Calibrate sensors and check connectivity",
                "priority": "low",
                "estimated_time_mins": 30
            }
        ]
        
        return {
            "project_id": project_id,
            "title": "Pre-Monsoon System Check",
            "recommended_date": f"Complete by May 31, {datetime.now().year}",
            "total_estimated_time_mins": sum(item["estimated_time_mins"] for item in checklist),
            "checklist": checklist
        }


# Singleton instance
_performance_service: Optional[PerformanceAnalyticsService] = None


def get_performance_service() -> PerformanceAnalyticsService:
    """Get or create performance analytics service instance."""
    global _performance_service
    if _performance_service is None:
        _performance_service = PerformanceAnalyticsService()
    return _performance_service
