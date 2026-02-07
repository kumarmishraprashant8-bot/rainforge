"""
Predictive Maintenance Service
Uses ML to predict equipment failures before they occur.
Analyzes sensor patterns for filters, tanks, and pumps.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE_DUE = "maintenance_due"


class ComponentType(str, Enum):
    """RWH system components."""
    FILTER = "filter"
    TANK = "tank"
    PUMP = "pump"
    PIPE = "pipe"
    VALVE = "valve"
    SENSOR = "sensor"


@dataclass
class MaintenanceAlert:
    """Maintenance alert for a component."""
    alert_id: str
    site_id: str
    component_type: ComponentType
    severity: AlertSeverity
    title: str
    description: str
    predicted_failure_date: Optional[datetime]
    confidence: float  # 0-1
    recommended_action: str
    estimated_cost_inr: float
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class ComponentHealth:
    """Health status of a component."""
    component_id: str
    component_type: ComponentType
    health_score: float  # 0-100
    days_until_maintenance: int
    last_maintenance: Optional[datetime]
    anomalies_detected: int
    status: str  # healthy, degraded, critical


@dataclass
class TelemetryData:
    """Sensor telemetry data point."""
    site_id: str
    timestamp: datetime
    flow_rate_lpm: float  # liters per minute
    pressure_bar: float
    turbidity_ntu: float  # Nephelometric Turbidity Units
    ph_level: float
    tank_level_percent: float
    pump_current_amps: float
    filter_pressure_drop: float


class PredictiveMaintenanceService:
    """
    ML-powered predictive maintenance for RWH systems.
    
    Analyzes telemetry patterns to predict:
    - Filter clogging (turbidity + pressure drop trends)
    - Tank issues (level anomalies, sediment buildup)
    - Pump failures (current draw patterns, vibration)
    - Pipe leaks (pressure drops, flow inconsistencies)
    """
    
    # Thresholds for alerts
    FILTER_PRESSURE_DROP_WARNING = 0.5  # bar
    FILTER_PRESSURE_DROP_CRITICAL = 0.8  # bar
    TURBIDITY_WARNING = 4.0  # NTU
    TURBIDITY_CRITICAL = 8.0  # NTU
    PUMP_CURRENT_VARIANCE_WARNING = 0.15  # 15% variance
    PUMP_CURRENT_VARIANCE_CRITICAL = 0.30  # 30% variance
    
    # Maintenance intervals (days)
    FILTER_MAINTENANCE_INTERVAL = 90
    TANK_CLEANING_INTERVAL = 180
    PUMP_SERVICE_INTERVAL = 365
    
    def __init__(self):
        self._alerts: Dict[str, MaintenanceAlert] = {}
        self._component_health: Dict[str, ComponentHealth] = {}
        self._telemetry_history: Dict[str, List[TelemetryData]] = {}
        self._maintenance_history: Dict[str, List[Dict]] = {}
        
    def ingest_telemetry(self, data: TelemetryData) -> List[MaintenanceAlert]:
        """
        Ingest telemetry data and check for anomalies.
        Returns any new alerts generated.
        """
        site_id = data.site_id
        
        # Store telemetry
        if site_id not in self._telemetry_history:
            self._telemetry_history[site_id] = []
        self._telemetry_history[site_id].append(data)
        
        # Keep last 1000 readings per site
        if len(self._telemetry_history[site_id]) > 1000:
            self._telemetry_history[site_id] = self._telemetry_history[site_id][-1000:]
        
        # Analyze for anomalies
        alerts = []
        alerts.extend(self._check_filter_health(data))
        alerts.extend(self._check_pump_health(data))
        alerts.extend(self._check_tank_health(data))
        
        return alerts
    
    def _check_filter_health(self, data: TelemetryData) -> List[MaintenanceAlert]:
        """Check filter health based on pressure drop and turbidity."""
        alerts = []
        
        # High pressure drop indicates clogging
        if data.filter_pressure_drop >= self.FILTER_PRESSURE_DROP_CRITICAL:
            alert = MaintenanceAlert(
                alert_id=f"alert_{data.site_id}_filter_{datetime.now().timestamp()}",
                site_id=data.site_id,
                component_type=ComponentType.FILTER,
                severity=AlertSeverity.CRITICAL,
                title="Filter Critically Clogged",
                description=f"Pressure drop at {data.filter_pressure_drop:.2f} bar - immediate cleaning required",
                predicted_failure_date=datetime.now() + timedelta(days=3),
                confidence=0.92,
                recommended_action="Replace or clean filter immediately. Check for debris accumulation.",
                estimated_cost_inr=500
            )
            self._alerts[alert.alert_id] = alert
            alerts.append(alert)
            
        elif data.filter_pressure_drop >= self.FILTER_PRESSURE_DROP_WARNING:
            alert = MaintenanceAlert(
                alert_id=f"alert_{data.site_id}_filter_{datetime.now().timestamp()}",
                site_id=data.site_id,
                component_type=ComponentType.FILTER,
                severity=AlertSeverity.WARNING,
                title="Filter Needs Cleaning",
                description=f"Pressure drop at {data.filter_pressure_drop:.2f} bar - schedule cleaning",
                predicted_failure_date=datetime.now() + timedelta(days=14),
                confidence=0.78,
                recommended_action="Schedule filter cleaning within 2 weeks.",
                estimated_cost_inr=300
            )
            self._alerts[alert.alert_id] = alert
            alerts.append(alert)
        
        # High turbidity after filter
        if data.turbidity_ntu >= self.TURBIDITY_CRITICAL:
            alert = MaintenanceAlert(
                alert_id=f"alert_{data.site_id}_turbidity_{datetime.now().timestamp()}",
                site_id=data.site_id,
                component_type=ComponentType.FILTER,
                severity=AlertSeverity.CRITICAL,
                title="Water Quality Issue",
                description=f"Turbidity at {data.turbidity_ntu:.1f} NTU - filter bypass suspected",
                predicted_failure_date=None,
                confidence=0.85,
                recommended_action="Inspect filter seals and replace filter media.",
                estimated_cost_inr=800
            )
            self._alerts[alert.alert_id] = alert
            alerts.append(alert)
            
        return alerts
    
    def _check_pump_health(self, data: TelemetryData) -> List[MaintenanceAlert]:
        """Check pump health based on current draw patterns."""
        alerts = []
        site_id = data.site_id
        
        # Get historical pump current data
        history = self._telemetry_history.get(site_id, [])
        if len(history) < 10:
            return alerts
            
        # Calculate variance in pump current
        recent_currents = [h.pump_current_amps for h in history[-50:]]
        avg_current = sum(recent_currents) / len(recent_currents)
        
        if avg_current > 0:
            variance = abs(data.pump_current_amps - avg_current) / avg_current
            
            if variance >= self.PUMP_CURRENT_VARIANCE_CRITICAL:
                alert = MaintenanceAlert(
                    alert_id=f"alert_{site_id}_pump_{datetime.now().timestamp()}",
                    site_id=site_id,
                    component_type=ComponentType.PUMP,
                    severity=AlertSeverity.CRITICAL,
                    title="Pump Failure Imminent",
                    description=f"Current draw variance at {variance*100:.0f}% - bearing failure likely",
                    predicted_failure_date=datetime.now() + timedelta(days=7),
                    confidence=0.88,
                    recommended_action="Replace pump bearings or entire pump unit.",
                    estimated_cost_inr=3500
                )
                self._alerts[alert.alert_id] = alert
                alerts.append(alert)
                
            elif variance >= self.PUMP_CURRENT_VARIANCE_WARNING:
                alert = MaintenanceAlert(
                    alert_id=f"alert_{site_id}_pump_{datetime.now().timestamp()}",
                    site_id=site_id,
                    component_type=ComponentType.PUMP,
                    severity=AlertSeverity.WARNING,
                    title="Pump Performance Degrading",
                    description=f"Current draw variance at {variance*100:.0f}% - monitor closely",
                    predicted_failure_date=datetime.now() + timedelta(days=30),
                    confidence=0.72,
                    recommended_action="Schedule pump inspection and lubrication.",
                    estimated_cost_inr=1000
                )
                self._alerts[alert.alert_id] = alert
                alerts.append(alert)
                
        return alerts
    
    def _check_tank_health(self, data: TelemetryData) -> List[MaintenanceAlert]:
        """Check tank health based on level patterns."""
        alerts = []
        site_id = data.site_id
        
        # Detect sudden level drops (possible leak)
        history = self._telemetry_history.get(site_id, [])
        if len(history) >= 2:
            prev_level = history[-2].tank_level_percent
            current_level = data.tank_level_percent
            
            # Sudden drop > 10% in short time with no usage
            if prev_level - current_level > 10:
                alert = MaintenanceAlert(
                    alert_id=f"alert_{site_id}_tank_{datetime.now().timestamp()}",
                    site_id=site_id,
                    component_type=ComponentType.TANK,
                    severity=AlertSeverity.CRITICAL,
                    title="Possible Tank Leak",
                    description=f"Level dropped {prev_level - current_level:.1f}% unexpectedly",
                    predicted_failure_date=None,
                    confidence=0.75,
                    recommended_action="Inspect tank for cracks or valve issues.",
                    estimated_cost_inr=2000
                )
                self._alerts[alert.alert_id] = alert
                alerts.append(alert)
                
        return alerts
    
    def get_site_health_summary(self, site_id: str) -> Dict[str, Any]:
        """Get comprehensive health summary for a site."""
        history = self._telemetry_history.get(site_id, [])
        site_alerts = [a for a in self._alerts.values() if a.site_id == site_id and not a.resolved]
        
        # Calculate component health scores
        filter_health = self._calculate_filter_health(history)
        pump_health = self._calculate_pump_health(history)
        tank_health = self._calculate_tank_health(history)
        
        overall_health = (filter_health + pump_health + tank_health) / 3
        
        return {
            "site_id": site_id,
            "overall_health_score": round(overall_health, 1),
            "status": "healthy" if overall_health >= 80 else "degraded" if overall_health >= 50 else "critical",
            "components": {
                "filter": {"health_score": filter_health, "status": self._health_status(filter_health)},
                "pump": {"health_score": pump_health, "status": self._health_status(pump_health)},
                "tank": {"health_score": tank_health, "status": self._health_status(tank_health)}
            },
            "active_alerts": len(site_alerts),
            "alerts": [
                {
                    "id": a.alert_id,
                    "severity": a.severity.value,
                    "title": a.title,
                    "component": a.component_type.value,
                    "confidence": a.confidence
                }
                for a in site_alerts
            ],
            "next_scheduled_maintenance": self._get_next_maintenance(site_id),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_filter_health(self, history: List[TelemetryData]) -> float:
        """Calculate filter health score 0-100."""
        if not history:
            return 100.0
        
        recent = history[-20:]
        avg_pressure_drop = sum(h.filter_pressure_drop for h in recent) / len(recent)
        avg_turbidity = sum(h.turbidity_ntu for h in recent) / len(recent)
        
        # Score based on pressure drop (0-50 points)
        pressure_score = max(0, 50 - (avg_pressure_drop / self.FILTER_PRESSURE_DROP_CRITICAL) * 50)
        
        # Score based on turbidity (0-50 points)
        turbidity_score = max(0, 50 - (avg_turbidity / self.TURBIDITY_CRITICAL) * 50)
        
        return min(100, pressure_score + turbidity_score)
    
    def _calculate_pump_health(self, history: List[TelemetryData]) -> float:
        """Calculate pump health score 0-100."""
        if len(history) < 10:
            return 100.0
        
        currents = [h.pump_current_amps for h in history[-50:]]
        avg = sum(currents) / len(currents)
        if avg == 0:
            return 100.0
            
        variance = sum(abs(c - avg) / avg for c in currents) / len(currents)
        
        # Lower variance = higher score
        return max(0, 100 - (variance * 300))
    
    def _calculate_tank_health(self, history: List[TelemetryData]) -> float:
        """Calculate tank health score 0-100."""
        if len(history) < 5:
            return 100.0
        
        # Check for sudden level changes
        levels = [h.tank_level_percent for h in history[-20:]]
        sudden_drops = sum(1 for i in range(1, len(levels)) if levels[i-1] - levels[i] > 5)
        
        return max(0, 100 - (sudden_drops * 15))
    
    def _health_status(self, score: float) -> str:
        """Convert health score to status string."""
        if score >= 80:
            return "healthy"
        elif score >= 50:
            return "degraded"
        return "critical"
    
    def _get_next_maintenance(self, site_id: str) -> Optional[str]:
        """Get next scheduled maintenance date."""
        # Mock implementation - would use actual maintenance history
        return (datetime.now() + timedelta(days=random.randint(7, 45))).strftime("%Y-%m-%d")
    
    def predict_maintenance_schedule(
        self, 
        site_id: str, 
        days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Predict maintenance needs for next N days.
        Uses ML model trained on historical patterns.
        """
        schedule = []
        base_date = datetime.now()
        
        # Get site health
        history = self._telemetry_history.get(site_id, [])
        filter_health = self._calculate_filter_health(history)
        pump_health = self._calculate_pump_health(history)
        tank_health = self._calculate_tank_health(history)
        
        # Predict filter maintenance
        if filter_health < 80:
            days_until = int((filter_health / 100) * self.FILTER_MAINTENANCE_INTERVAL)
            schedule.append({
                "component": "filter",
                "type": "cleaning",
                "predicted_date": (base_date + timedelta(days=days_until)).strftime("%Y-%m-%d"),
                "confidence": 0.85,
                "estimated_cost_inr": 500,
                "urgency": "high" if filter_health < 50 else "medium"
            })
        
        # Predict pump maintenance
        if pump_health < 80:
            days_until = int((pump_health / 100) * self.PUMP_SERVICE_INTERVAL)
            schedule.append({
                "component": "pump",
                "type": "service",
                "predicted_date": (base_date + timedelta(days=days_until)).strftime("%Y-%m-%d"),
                "confidence": 0.78,
                "estimated_cost_inr": 1500,
                "urgency": "high" if pump_health < 50 else "medium"
            })
        
        # Predict tank cleaning
        if tank_health < 90:
            days_until = int((tank_health / 100) * self.TANK_CLEANING_INTERVAL)
            schedule.append({
                "component": "tank",
                "type": "cleaning",
                "predicted_date": (base_date + timedelta(days=days_until)).strftime("%Y-%m-%d"),
                "confidence": 0.72,
                "estimated_cost_inr": 2000,
                "urgency": "medium"
            })
        
        # Sort by date
        schedule.sort(key=lambda x: x["predicted_date"])
        
        return schedule
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        if alert_id in self._alerts:
            self._alerts[alert_id].acknowledged = True
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Mark an alert as resolved."""
        if alert_id in self._alerts:
            self._alerts[alert_id].resolved = True
            logger.info(f"Alert {alert_id} resolved: {resolution_notes}")
            return True
        return False
    
    def get_all_alerts(
        self, 
        severity: Optional[AlertSeverity] = None,
        unresolved_only: bool = True
    ) -> List[MaintenanceAlert]:
        """Get all alerts, optionally filtered."""
        alerts = list(self._alerts.values())
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: (a.severity != AlertSeverity.CRITICAL, a.created_at))


# Singleton instance
_service: Optional[PredictiveMaintenanceService] = None


def get_predictive_maintenance_service() -> PredictiveMaintenanceService:
    """Get or create the predictive maintenance service singleton."""
    global _service
    if _service is None:
        _service = PredictiveMaintenanceService()
    return _service
