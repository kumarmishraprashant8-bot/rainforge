"""
Analytics Dashboard Service
Aggregated metrics and insights
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class TimeRange(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


@dataclass
class DashboardCard:
    """Dashboard summary card."""
    id: str
    title: str
    value: Any
    change: float  # Percentage change
    change_direction: str  # up, down, neutral
    icon: str
    color: str


@dataclass
class ChartData:
    """Chart data structure."""
    labels: List[str]
    datasets: List[Dict[str, Any]]


class AnalyticsDashboardService:
    """
    Analytics dashboard with aggregated metrics.
    
    Provides:
    - Summary cards
    - Time-series charts
    - Geographic distribution
    - Performance metrics
    - Export capabilities
    """
    
    def __init__(self):
        # In-memory metrics store (would be database in production)
        self._metrics: Dict[str, List[Dict]] = {}
        self._daily_stats: Dict[str, Dict] = {}
    
    async def get_dashboard_summary(
        self,
        tenant_id: Optional[str] = None,
        time_range: TimeRange = TimeRange.MONTH
    ) -> Dict[str, Any]:
        """Get dashboard summary with key metrics."""
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = self._get_start_date(time_range)
        prev_start = start_date - (end_date - start_date)
        
        # Get current and previous period data (mock data for now)
        current_data = await self._get_period_data(start_date, end_date, tenant_id)
        previous_data = await self._get_period_data(prev_start, start_date, tenant_id)
        
        # Calculate cards
        cards = [
            self._create_card(
                "total_projects",
                "Total Projects",
                current_data.get("projects", 1247),
                previous_data.get("projects", 1180),
                "📊",
                "#0ea5e9"
            ),
            self._create_card(
                "water_collected",
                "Water Collected (ML)",
                current_data.get("water_collected_ml", 45.2),
                previous_data.get("water_collected_ml", 38.5),
                "💧",
                "#10b981"
            ),
            self._create_card(
                "active_sensors",
                "Active Sensors",
                current_data.get("active_sensors", 892),
                previous_data.get("active_sensors", 756),
                "📡",
                "#7c3aed"
            ),
            self._create_card(
                "carbon_offset",
                "CO₂ Offset (tons)",
                current_data.get("carbon_offset", 234),
                previous_data.get("carbon_offset", 198),
                "🌱",
                "#22c55e"
            ),
            self._create_card(
                "verified_installations",
                "Verified Installations",
                current_data.get("verified", 987),
                previous_data.get("verified", 845),
                "✅",
                "#f59e0b"
            ),
            self._create_card(
                "subsidy_disbursed",
                "Subsidy Disbursed (₹L)",
                current_data.get("subsidy_lakhs", 127.5),
                previous_data.get("subsidy_lakhs", 105.2),
                "💰",
                "#ef4444"
            )
        ]
        
        return {
            "period": time_range.value,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "cards": [self._card_to_dict(c) for c in cards],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def get_installation_trend(
        self,
        time_range: TimeRange = TimeRange.MONTH,
        granularity: str = "day"
    ) -> ChartData:
        """Get installation trend chart data."""
        days = self._get_days(time_range)
        labels = []
        values = []
        cumulative = []
        
        import random
        total = 0
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-1-i)
            labels.append(date.strftime("%b %d"))
            
            # Mock data with realistic pattern
            base = 15 + i * 0.5
            variance = random.uniform(-5, 10)
            day_value = max(0, int(base + variance))
            values.append(day_value)
            total += day_value
            cumulative.append(total)
        
        return ChartData(
            labels=labels,
            datasets=[
                {
                    "label": "Daily Installations",
                    "data": values,
                    "borderColor": "#0ea5e9",
                    "backgroundColor": "rgba(14, 165, 233, 0.1)",
                    "fill": True
                },
                {
                    "label": "Cumulative",
                    "data": cumulative,
                    "borderColor": "#7c3aed",
                    "borderDash": [5, 5],
                    "fill": False
                }
            ]
        )
    
    async def get_water_savings_chart(
        self,
        time_range: TimeRange = TimeRange.MONTH
    ) -> ChartData:
        """Get water savings chart data."""
        days = self._get_days(time_range)
        labels = []
        collected = []
        saved = []
        
        import random
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-1-i)
            labels.append(date.strftime("%b %d"))
            
            # Water collected varies with "rain patterns"
            rain_factor = 0.5 + 0.5 * (1 + random.uniform(-0.3, 0.3) + 0.3 * (i % 7 < 2))
            day_collected = int(50000 * rain_factor)  # liters
            collected.append(day_collected)
            saved.append(int(day_collected * 0.4))  # Municipal water saved
        
        return ChartData(
            labels=labels,
            datasets=[
                {
                    "label": "Rainwater Collected (L)",
                    "data": collected,
                    "backgroundColor": "#0ea5e9"
                },
                {
                    "label": "Municipal Water Saved (L)",
                    "data": saved,
                    "backgroundColor": "#22c55e"
                }
            ]
        )
    
    async def get_geographic_distribution(
        self,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get geographic distribution of installations."""
        # Mock data for Indian states
        return {
            "type": "choropleth",
            "data": [
                {"state": "Maharashtra", "count": 342, "lat": 19.7515, "lng": 75.7139},
                {"state": "Karnataka", "count": 289, "lat": 15.3173, "lng": 75.7139},
                {"state": "Tamil Nadu", "count": 264, "lat": 11.1271, "lng": 78.6569},
                {"state": "Gujarat", "count": 198, "lat": 22.2587, "lng": 71.1924},
                {"state": "Rajasthan", "count": 156, "lat": 27.0238, "lng": 74.2179},
                {"state": "Kerala", "count": 145, "lat": 10.8505, "lng": 76.2711},
                {"state": "Andhra Pradesh", "count": 134, "lat": 15.9129, "lng": 79.7400},
                {"state": "Telangana", "count": 128, "lat": 18.1124, "lng": 79.0193},
                {"state": "Madhya Pradesh", "count": 98, "lat": 22.9734, "lng": 78.6569},
                {"state": "Uttar Pradesh", "count": 87, "lat": 26.8467, "lng": 80.9462}
            ],
            "total": 1841,
            "top_district": {
                "name": "Pune",
                "state": "Maharashtra",
                "count": 89
            }
        }
    
    async def get_installer_performance(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top installer performance."""
        # Mock data
        import random
        
        installers = [
            "RWH Solutions Pvt Ltd",
            "Green Water Systems",
            "EcoHarvest India",
            "AquaSave Technologies",
            "JalSanchay Enterprises",
            "RainMasters Co.",
            "WaterWise Solutions",
            "Monsoon Tech",
            "HydroStore Systems",
            "VarshaJal Industries"
        ]
        
        return [
            {
                "rank": i + 1,
                "name": installers[i],
                "projects_completed": random.randint(45, 120),
                "average_rating": round(random.uniform(4.2, 4.9), 1),
                "total_capacity_kl": random.randint(500, 2000),
                "on_time_percentage": random.randint(85, 98),
                "verified": True
            }
            for i in range(limit)
        ]
    
    async def get_verification_stats(
        self,
        time_range: TimeRange = TimeRange.MONTH
    ) -> Dict[str, Any]:
        """Get verification statistics."""
        return {
            "total_submitted": 456,
            "pending": 23,
            "approved": 412,
            "rejected": 21,
            "approval_rate": 95.1,
            "average_time_hours": 18.5,
            "by_photo_type": {
                "pre_installation": 456,
                "during_installation": 412,
                "post_installation": 389,
                "first_rain": 234
            },
            "fraud_detected": 3,
            "duplicate_photos": 7
        }
    
    async def get_payment_analytics(
        self,
        time_range: TimeRange = TimeRange.MONTH
    ) -> Dict[str, Any]:
        """Get payment and subsidy analytics."""
        return {
            "total_disbursed": 12750000,  # INR
            "pending": 2340000,
            "average_per_project": 25000,
            "by_category": {
                "residential_small": 4500000,
                "residential_large": 3200000,
                "commercial": 2800000,
                "industrial": 2250000
            },
            "payment_methods": {
                "bank_transfer": 78,
                "upi": 15,
                "cheque": 7
            },
            "average_processing_days": 5.2
        }
    
    async def get_sensor_health(self) -> Dict[str, Any]:
        """Get IoT sensor health overview."""
        return {
            "total_sensors": 892,
            "online": 845,
            "offline": 47,
            "uptime_percent": 94.7,
            "by_type": {
                "tank_level": 456,
                "flow_meter": 234,
                "rain_gauge": 156,
                "temperature": 46
            },
            "alerts_today": 12,
            "maintenance_due": 28
        }
    
    async def export_report(
        self,
        report_type: str,
        time_range: TimeRange,
        format: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate exportable report."""
        # In production, would generate actual PDF/Excel
        return {
            "report_id": f"rpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": report_type,
            "period": time_range.value,
            "format": format,
            "status": "generating",
            "estimated_time_seconds": 30,
            "download_url": None  # Would be populated when ready
        }
    
    # ==================== HELPERS ====================
    
    def _get_start_date(self, time_range: TimeRange) -> datetime:
        """Get start date for time range."""
        now = datetime.utcnow()
        
        if time_range == TimeRange.TODAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == TimeRange.WEEK:
            return now - timedelta(days=7)
        elif time_range == TimeRange.MONTH:
            return now - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return now - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=365*5)  # 5 years
    
    def _get_days(self, time_range: TimeRange) -> int:
        """Get number of days for time range."""
        mapping = {
            TimeRange.TODAY: 1,
            TimeRange.WEEK: 7,
            TimeRange.MONTH: 30,
            TimeRange.QUARTER: 90,
            TimeRange.YEAR: 365,
            TimeRange.ALL_TIME: 365
        }
        return mapping.get(time_range, 30)
    
    async def _get_period_data(
        self,
        start: datetime,
        end: datetime,
        tenant_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get aggregated data for period (mock)."""
        import random
        
        days = (end - start).days
        base_multiplier = days / 30
        
        return {
            "projects": int(1200 * base_multiplier + random.randint(-50, 100)),
            "water_collected_ml": round(40 * base_multiplier + random.uniform(-5, 10), 1),
            "active_sensors": int(800 * base_multiplier + random.randint(-50, 100)),
            "carbon_offset": int(200 * base_multiplier + random.randint(-20, 50)),
            "verified": int(900 * base_multiplier + random.randint(-50, 100)),
            "subsidy_lakhs": round(100 * base_multiplier + random.uniform(-10, 30), 1)
        }
    
    def _create_card(
        self,
        id: str,
        title: str,
        current: float,
        previous: float,
        icon: str,
        color: str
    ) -> DashboardCard:
        """Create dashboard card with change calculation."""
        if previous > 0:
            change = ((current - previous) / previous) * 100
        else:
            change = 100 if current > 0 else 0
        
        return DashboardCard(
            id=id,
            title=title,
            value=current,
            change=round(change, 1),
            change_direction="up" if change > 0 else "down" if change < 0 else "neutral",
            icon=icon,
            color=color
        )
    
    def _card_to_dict(self, card: DashboardCard) -> Dict:
        """Convert card to dictionary."""
        return {
            "id": card.id,
            "title": card.title,
            "value": card.value,
            "change": card.change,
            "changeDirection": card.change_direction,
            "icon": card.icon,
            "color": card.color
        }


# Singleton
_analytics: Optional[AnalyticsDashboardService] = None

def get_analytics_service() -> AnalyticsDashboardService:
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsDashboardService()
    return _analytics
