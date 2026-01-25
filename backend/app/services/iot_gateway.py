"""
RainForge IoT Gateway Service
MQTT-ready architecture for sensor integration with simulated data.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import math


class IoTGateway:
    """
    IoT Gateway for RWH monitoring sensors.
    Currently provides simulated data; production would use MQTT broker.
    """
    
    # Simulated sensor configs
    SENSOR_CONFIG = {
        "tank_level": {"min": 0, "max": 100, "unit": "%"},
        "flow_rate": {"min": 0, "max": 50, "unit": "lpm"},
        "rainfall": {"min": 0, "max": 20, "unit": "mm"},
        "temperature": {"min": 15, "max": 45, "unit": "°C"},
    }
    
    # Maintenance thresholds
    ALERT_THRESHOLDS = {
        "tank_low": 20,       # Alert if < 20%
        "tank_overflow": 95,   # Alert if > 95%
        "no_data": 3600,      # Alert if no reading for 1 hour
        "filter_check_days": 30,
    }
    
    @staticmethod
    def get_current_reading(project_id: int, simulate: bool = True) -> Dict:
        """
        Get current sensor reading for a project.
        In production, this would query MQTT broker or database.
        """
        if simulate:
            # Simulate realistic tank level based on time of day
            hour = datetime.now().hour
            base_level = 60 + 20 * math.sin(hour * math.pi / 12)  # Peaks at noon
            level = max(5, min(95, base_level + random.uniform(-10, 10)))
            
            # Simulate flow rate (higher in morning/evening)
            if 6 <= hour <= 9 or 17 <= hour <= 21:
                flow = random.uniform(5, 20)
            else:
                flow = random.uniform(0, 5)
            
            # Simulate rainfall (random, more likely in monsoon months)
            month = datetime.now().month
            if 6 <= month <= 9:  # Monsoon
                rain = random.uniform(0, 10) if random.random() < 0.3 else 0
            else:
                rain = random.uniform(0, 2) if random.random() < 0.1 else 0
            
            return {
                "project_id": project_id,
                "tank_level_percent": round(level, 1),
                "tank_volume_liters": round(level * 100),  # Assuming 10000L tank
                "flow_rate_lpm": round(flow, 2),
                "rainfall_mm": round(rain, 1),
                "temperature_c": round(25 + random.uniform(-5, 10), 1),
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_status": "online",
                "battery_percent": random.randint(60, 100)
            }
        
        # Production: Query actual sensor data
        return {"error": "Real sensors not connected"}
    
    @staticmethod
    def get_historical_readings(
        project_id: int,
        hours: int = 24,
        interval_minutes: int = 60
    ) -> List[Dict]:
        """
        Get historical readings for charting.
        """
        readings = []
        now = datetime.utcnow()
        
        for i in range(0, hours * 60, interval_minutes):
            time_point = now - timedelta(minutes=i)
            hour = time_point.hour
            
            # Simulate with daily pattern
            base_level = 60 + 20 * math.sin(hour * math.pi / 12)
            level = max(5, min(95, base_level + random.uniform(-5, 5)))
            
            readings.append({
                "timestamp": time_point.isoformat(),
                "tank_level_percent": round(level, 1),
                "flow_rate_lpm": round(random.uniform(0, 15), 2),
                "rainfall_mm": round(random.uniform(0, 3), 1)
            })
        
        return list(reversed(readings))
    
    @staticmethod
    def check_alerts(project_id: int, current_reading: Dict) -> List[Dict]:
        """
        Check reading against thresholds and generate alerts.
        """
        alerts = []
        
        level = current_reading.get("tank_level_percent", 50)
        
        if level < IoTGateway.ALERT_THRESHOLDS["tank_low"]:
            alerts.append({
                "type": "warning",
                "code": "TANK_LOW",
                "message": f"Tank level critically low ({level}%). Consider water conservation.",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if level > IoTGateway.ALERT_THRESHOLDS["tank_overflow"]:
            alerts.append({
                "type": "warning", 
                "code": "TANK_OVERFLOW_RISK",
                "message": f"Tank near capacity ({level}%). Overflow likely with next rainfall.",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Maintenance reminder (mock based on random)
        if random.random() < 0.1:
            alerts.append({
                "type": "info",
                "code": "FILTER_CHECK",  
                "message": "Monthly filter inspection due. Check first-flush diverter.",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    @staticmethod
    def get_tank_status(project_id: int, tank_capacity: float = 10000) -> Dict:
        """
        Get comprehensive tank status with predictions.
        """
        reading = IoTGateway.get_current_reading(project_id)
        alerts = IoTGateway.check_alerts(project_id, reading)
        
        level = reading["tank_level_percent"]
        current_volume = tank_capacity * level / 100
        
        # Predict empty date based on usage pattern
        avg_daily_usage = 200  # liters
        days_remaining = current_volume / avg_daily_usage if avg_daily_usage > 0 else 365
        predicted_empty = datetime.now() + timedelta(days=days_remaining)
        
        return {
            "project_id": project_id,
            "current_level_percent": level,
            "current_volume_liters": round(current_volume),
            "capacity_liters": tank_capacity,
            "last_updated": reading["timestamp"],
            "sensor_status": reading["sensor_status"],
            "predicted_empty_date": predicted_empty.isoformat() if days_remaining < 30 else None,
            "days_until_empty": round(days_remaining, 1),
            "maintenance_alerts": [a["message"] for a in alerts]
        }
    
    @staticmethod
    def get_portfolio_monitoring(project_ids: List[int]) -> Dict:
        """
        Get monitoring summary for multiple projects (portfolio view).
        """
        projects = []
        total_volume = 0
        total_capacity = 0
        online_count = 0
        all_alerts = []
        
        for pid in project_ids:
            status = IoTGateway.get_tank_status(pid)
            projects.append(status)
            
            total_volume += status["current_volume_liters"]
            total_capacity += status["capacity_liters"]
            
            if status["sensor_status"] == "online":
                online_count += 1
            
            all_alerts.extend(status["maintenance_alerts"])
        
        return {
            "total_projects": len(project_ids),
            "online_projects": online_count,
            "offline_projects": len(project_ids) - online_count,
            "total_stored_liters": round(total_volume),
            "total_capacity_liters": round(total_capacity),
            "avg_tank_level_percent": round((total_volume / total_capacity * 100) if total_capacity > 0 else 0, 1),
            "alerts_count": len(all_alerts),
            "recent_alerts": all_alerts[:5],  # Top 5 alerts
            "projects": projects
        }


class MQTTConfig:
    """
    MQTT configuration for production deployment.
    """
    BROKER_HOST = "mqtt.rainforge.gov.in"
    BROKER_PORT = 1883
    TOPIC_PREFIX = "rainforge/sensors"
    
    # Topic structure:
    # rainforge/sensors/{project_id}/tank_level
    # rainforge/sensors/{project_id}/flow_rate
    # rainforge/sensors/{project_id}/rainfall
    # rainforge/sensors/{project_id}/status
    
    @staticmethod
    def get_topic(project_id: int, sensor_type: str) -> str:
        return f"{MQTTConfig.TOPIC_PREFIX}/{project_id}/{sensor_type}"
