"""
Enhanced IoT Service
Device pairing, calibration, leak detection, and overflow prediction.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
import hashlib
import random
import base64

logger = logging.getLogger(__name__)


@dataclass 
class DeviceInfo:
    """IoT device information."""
    device_id: str
    device_type: str
    device_serial: str
    project_id: int
    paired_at: datetime
    calibrated: bool
    last_seen: Optional[datetime]
    status: str


class EnhancedIoTService:
    """
    Enhanced IoT service with advanced features.
    
    Features:
    - Device pairing via QR code
    - Tank calibration wizard
    - Leak detection algorithm
    - Overflow prediction
    - First flush trigger logging
    - Multi-sensor correlation
    """
    
    # Device types
    DEVICE_TYPES = {
        "tank_sensor": {
            "name": "Tank Level Sensor",
            "readings": ["level_cm", "level_percent", "volume_liters"],
            "calibration_required": True
        },
        "flow_meter": {
            "name": "Flow Meter",
            "readings": ["flow_rate_lpm", "total_volume_liters"],
            "calibration_required": True
        },
        "quality_sensor": {
            "name": "Water Quality Sensor",
            "readings": ["ph", "tds_ppm", "turbidity_ntu", "temperature_c"],
            "calibration_required": False
        },
        "rain_gauge": {
            "name": "Rain Gauge",
            "readings": ["rainfall_mm", "intensity_mm_hr"],
            "calibration_required": False
        },
        "first_flush": {
            "name": "First Flush Sensor",
            "readings": ["triggered", "diversion_liters"],
            "calibration_required": False
        }
    }
    
    def __init__(self):
        self.devices: Dict[str, Dict] = {}
        self.calibrations: Dict[str, Dict] = {}
        self.readings: Dict[str, List[Dict]] = {}
        self.alerts: Dict[str, List[Dict]] = {}
        self.first_flush_logs: Dict[int, List[Dict]] = {}
    
    # ==================== DEVICE PAIRING ====================
    
    def generate_pairing_qr(
        self,
        project_id: int,
        device_type: str
    ) -> Dict[str, Any]:
        """Generate QR code for device pairing."""
        
        if device_type not in self.DEVICE_TYPES:
            raise ValueError(f"Unknown device type: {device_type}")
        
        # Generate pairing token
        token = hashlib.sha256(
            f"{project_id}-{device_type}-{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Create pairing data
        pairing_data = {
            "project_id": project_id,
            "device_type": device_type,
            "token": token,
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "api_endpoint": "/api/v1/iot/device/pair",
            "format": "rainforge-v1"
        }
        
        # Encode as QR data
        qr_data = base64.b64encode(str(pairing_data).encode()).decode()
        
        return {
            "pairing_id": token,
            "qr_data": qr_data,
            "qr_url": f"rainforge://pair?token={token}",
            "expires_at": pairing_data["expires_at"],
            "device_type": device_type,
            "device_name": self.DEVICE_TYPES[device_type]["name"],
            "instructions": [
                "1. Power on the device",
                "2. Press and hold the pair button for 3 seconds",
                "3. Scan this QR code with the device app",
                "4. Wait for confirmation LED to turn green"
            ]
        }
    
    def pair_device(
        self,
        project_id: int,
        device_type: str,
        device_serial: str,
        device_name: Optional[str] = None,
        pairing_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pair a new IoT device."""
        
        if device_type not in self.DEVICE_TYPES:
            raise ValueError(f"Unknown device type: {device_type}")
        
        device_id = f"DEV-{project_id}-{device_type[:3].upper()}-{device_serial[-6:]}"
        
        device = {
            "device_id": device_id,
            "project_id": project_id,
            "device_type": device_type,
            "device_serial": device_serial,
            "device_name": device_name or f"{self.DEVICE_TYPES[device_type]['name']} #{device_serial[-4:]}",
            
            "paired_at": datetime.utcnow().isoformat(),
            "calibrated": False,
            "calibration_data": None,
            
            "status": "online",
            "last_seen": datetime.utcnow().isoformat(),
            "firmware_version": "1.0.0",
            
            "settings": {
                "reading_interval_seconds": 300,  # 5 minutes
                "alert_threshold_low": 10,  # 10% tank level
                "alert_threshold_high": 95  # 95% tank level
            }
        }
        
        self.devices[device_id] = device
        
        logger.info(f"Paired device {device_id} for project {project_id}")
        
        return device
    
    def get_project_devices(self, project_id: int) -> List[Dict]:
        """Get all devices for a project."""
        return [
            d for d in self.devices.values()
            if d["project_id"] == project_id
        ]
    
    # ==================== CALIBRATION ====================
    
    def start_calibration(
        self,
        device_id: str,
        tank_capacity_liters: int,
        tank_shape: str = "cylindrical"
    ) -> Dict[str, Any]:
        """Start calibration wizard for tank sensor."""
        
        if device_id not in self.devices:
            raise ValueError(f"Device not found: {device_id}")
        
        device = self.devices[device_id]
        
        if device["device_type"] != "tank_sensor":
            raise ValueError("Calibration only available for tank sensors")
        
        calibration_id = f"CAL-{device_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Calibration steps
        steps = [
            {
                "step": 1,
                "instruction": "Ensure tank is EMPTY",
                "action": "record_empty",
                "completed": False
            },
            {
                "step": 2,
                "instruction": "Fill tank with known quantity (e.g., 1000 liters)",
                "action": "record_partial",
                "completed": False
            },
            {
                "step": 3,
                "instruction": "Fill tank to FULL capacity",
                "action": "record_full",
                "completed": False
            }
        ]
        
        calibration = {
            "calibration_id": calibration_id,
            "device_id": device_id,
            "tank_capacity_liters": tank_capacity_liters,
            "tank_shape": tank_shape,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "steps": steps,
            "readings": {},
            "calculated_params": None
        }
        
        self.calibrations[calibration_id] = calibration
        
        return calibration
    
    def record_calibration_point(
        self,
        calibration_id: str,
        step: int,
        sensor_reading: float,
        known_volume_liters: float = 0
    ) -> Dict[str, Any]:
        """Record a calibration point."""
        
        if calibration_id not in self.calibrations:
            raise ValueError(f"Calibration not found: {calibration_id}")
        
        calibration = self.calibrations[calibration_id]
        
        # Store reading
        calibration["readings"][f"step_{step}"] = {
            "sensor_reading": sensor_reading,
            "known_volume_liters": known_volume_liters,
            "recorded_at": datetime.utcnow().isoformat()
        }
        
        # Mark step complete
        for s in calibration["steps"]:
            if s["step"] == step:
                s["completed"] = True
                break
        
        # Check if all steps complete
        if all(s["completed"] for s in calibration["steps"]):
            calibration = self._complete_calibration(calibration_id)
        
        return calibration
    
    def _complete_calibration(self, calibration_id: str) -> Dict:
        """Complete calibration and calculate parameters."""
        
        calibration = self.calibrations[calibration_id]
        readings = calibration["readings"]
        
        # Calculate linear mapping parameters
        empty_reading = readings["step_1"]["sensor_reading"]
        full_reading = readings["step_3"]["sensor_reading"]
        
        # Sensor reading range
        reading_range = full_reading - empty_reading
        
        # Calculate scale factor (liters per sensor unit)
        scale_factor = calibration["tank_capacity_liters"] / reading_range if reading_range != 0 else 1
        
        calibration["calculated_params"] = {
            "empty_reading": empty_reading,
            "full_reading": full_reading,
            "scale_factor": scale_factor,
            "offset": empty_reading,
            "tank_capacity_liters": calibration["tank_capacity_liters"]
        }
        
        calibration["status"] = "completed"
        calibration["completed_at"] = datetime.utcnow().isoformat()
        
        # Update device calibration status
        device_id = calibration["device_id"]
        if device_id in self.devices:
            self.devices[device_id]["calibrated"] = True
            self.devices[device_id]["calibration_data"] = calibration["calculated_params"]
        
        logger.info(f"Calibration completed for {device_id}")
        
        return calibration
    
    def convert_reading_to_volume(
        self,
        device_id: str,
        sensor_reading: float
    ) -> Dict[str, float]:
        """Convert raw sensor reading to volume using calibration."""
        
        if device_id not in self.devices:
            raise ValueError(f"Device not found: {device_id}")
        
        device = self.devices[device_id]
        cal = device.get("calibration_data")
        
        if not cal:
            raise ValueError(f"Device not calibrated: {device_id}")
        
        # Apply calibration
        adjusted_reading = sensor_reading - cal["offset"]
        volume_liters = adjusted_reading * cal["scale_factor"]
        level_percent = (volume_liters / cal["tank_capacity_liters"]) * 100
        
        return {
            "raw_reading": sensor_reading,
            "volume_liters": max(0, min(cal["tank_capacity_liters"], volume_liters)),
            "level_percent": max(0, min(100, level_percent)),
            "capacity_liters": cal["tank_capacity_liters"]
        }
    
    # ==================== LEAK DETECTION ====================
    
    def detect_leak(
        self,
        project_id: int,
        readings_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Run leak detection algorithm on recent readings."""
        
        # Get last 24 hours of readings
        device_ids = [d["device_id"] for d in self.get_project_devices(project_id) if d["device_type"] == "tank_sensor"]
        
        if not device_ids:
            return {"leak_detected": False, "message": "No tank sensor found"}
        
        device_id = device_ids[0]
        
        # Simulate getting readings (in production, query from database)
        readings = readings_history or self._get_simulated_readings(device_id)
        
        if len(readings) < 10:
            return {"leak_detected": False, "message": "Insufficient data for analysis"}
        
        # Analyze for unexpected drops
        drops = []
        for i in range(1, len(readings)):
            time_diff_hours = (
                datetime.fromisoformat(readings[i]["timestamp"]) -
                datetime.fromisoformat(readings[i-1]["timestamp"])
            ).total_seconds() / 3600
            
            level_diff = readings[i-1]["level_percent"] - readings[i]["level_percent"]
            
            # Flag unexpected drops (> 5% per hour without usage/rainfall)
            if level_diff > 5 and time_diff_hours < 2:
                drops.append({
                    "from_time": readings[i-1]["timestamp"],
                    "to_time": readings[i]["timestamp"],
                    "drop_percent": level_diff
                })
        
        if drops:
            # Estimate loss rate
            total_drop = sum(d["drop_percent"] for d in drops)
            hours_analyzed = 24
            
            device = self.devices.get(device_id, {})
            cal = device.get("calibration_data", {})
            capacity = cal.get("tank_capacity_liters", 10000)
            
            estimated_loss_liters_per_day = (total_drop / 100) * capacity
            
            # Generate alert
            alert = {
                "alert_id": f"LEAK-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "project_id": project_id,
                "device_id": device_id,
                "alert_type": "leak_detected",
                "severity": "warning",
                "message": f"Potential leak detected: ~{int(estimated_loss_liters_per_day)} liters/day",
                "triggered_at": datetime.utcnow().isoformat(),
                "data": {
                    "consecutive_drops": len(drops),
                    "total_drop_percent": total_drop,
                    "estimated_loss_liters_per_day": estimated_loss_liters_per_day
                }
            }
            
            if project_id not in self.alerts:
                self.alerts[project_id] = []
            self.alerts[project_id].append(alert)
            
            return {
                "leak_detected": True,
                "leak_location": "unknown",
                "estimated_loss_liters_per_day": int(estimated_loss_liters_per_day),
                "consecutive_readings": len(drops),
                "confidence": "medium" if len(drops) < 5 else "high",
                "detected_at": datetime.utcnow().isoformat(),
                "recommendation": "Inspect tank, pipes, and connections for leaks"
            }
        
        return {
            "leak_detected": False,
            "message": "No leak detected in last 24 hours",
            "readings_analyzed": len(readings)
        }
    
    def _get_simulated_readings(self, device_id: str) -> List[Dict]:
        """Generate simulated readings for testing."""
        readings = []
        base_level = 70
        
        for i in range(48):  # 2 readings per hour for 24 hours
            timestamp = datetime.utcnow() - timedelta(hours=24-i/2)
            level = base_level + random.uniform(-2, 2)  # Normal variation
            
            readings.append({
                "device_id": device_id,
                "timestamp": timestamp.isoformat(),
                "level_percent": level
            })
        
        return readings
    
    # ==================== OVERFLOW PREDICTION ====================
    
    def predict_overflow(
        self,
        project_id: int,
        current_level_percent: float,
        tank_capacity_liters: int,
        expected_rainfall_mm: float,
        roof_area_sqm: float,
        runoff_coefficient: float = 0.85
    ) -> Dict[str, Any]:
        """Predict tank overflow based on weather forecast."""
        
        # Calculate expected collection
        expected_collection_liters = (
            roof_area_sqm * expected_rainfall_mm * runoff_coefficient
        )
        
        # Current volume
        current_volume = tank_capacity_liters * current_level_percent / 100
        
        # Available capacity
        available_capacity = tank_capacity_liters - current_volume
        
        # Will overflow?
        will_overflow = expected_collection_liters > available_capacity
        
        # Time to overflow (if rain starts now, assuming constant rate over 6 hours)
        if will_overflow:
            fill_rate_per_hour = expected_collection_liters / 6
            volume_to_fill = available_capacity
            hours_until_overflow = volume_to_fill / fill_rate_per_hour if fill_rate_per_hour > 0 else 0
            predicted_overflow_time = datetime.utcnow() + timedelta(hours=hours_until_overflow)
        else:
            hours_until_overflow = None
            predicted_overflow_time = None
        
        result = {
            "project_id": project_id,
            "analysis_time": datetime.utcnow().isoformat(),
            
            # Current state
            "current_level_percent": current_level_percent,
            "current_volume_liters": int(current_volume),
            "tank_capacity_liters": tank_capacity_liters,
            "available_capacity_liters": int(available_capacity),
            
            # Expected
            "expected_rainfall_mm": expected_rainfall_mm,
            "expected_collection_liters": int(expected_collection_liters),
            
            # Prediction
            "will_overflow": will_overflow,
            "hours_until_overflow": round(hours_until_overflow, 1) if hours_until_overflow else None,
            "predicted_overflow_time": predicted_overflow_time.isoformat() if predicted_overflow_time else None,
            "overflow_volume_liters": int(max(0, expected_collection_liters - available_capacity)),
            
            # Recommendation
            "recommended_action": self._get_overflow_recommendation(
                will_overflow, hours_until_overflow, current_level_percent
            )
        }
        
        # Generate alert if overflow imminent
        if will_overflow and hours_until_overflow and hours_until_overflow < 6:
            self._generate_overflow_alert(project_id, result)
        
        return result
    
    def _get_overflow_recommendation(
        self,
        will_overflow: bool,
        hours: Optional[float],
        current_level: float
    ) -> str:
        """Get recommendation based on overflow prediction."""
        
        if not will_overflow:
            return "No action needed. Tank can accommodate expected rainfall."
        
        if hours and hours < 2:
            return "URGENT: Overflow imminent. Use water now or open overflow valve."
        elif hours and hours < 6:
            return "Consider using stored water before rainfall to maximize capture."
        elif current_level > 80:
            return "Tank nearly full. Monitor during rainfall and use overflow for recharge."
        else:
            return "Plan water usage to create space for incoming rainfall."
    
    def _generate_overflow_alert(self, project_id: int, prediction: Dict):
        """Generate overflow alert."""
        alert = {
            "alert_id": f"OVERFLOW-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "alert_type": "tank_overflow",
            "severity": "warning",
            "message": f"Tank overflow predicted in {prediction['hours_until_overflow']:.1f} hours",
            "triggered_at": datetime.utcnow().isoformat(),
            "data": prediction
        }
        
        if project_id not in self.alerts:
            self.alerts[project_id] = []
        self.alerts[project_id].append(alert)
    
    # ==================== FIRST FLUSH LOGGING ====================
    
    def log_first_flush_trigger(
        self,
        project_id: int,
        device_id: str,
        diversion_liters: float,
        rainfall_mm: float,
        trigger_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Log first flush diverter trigger event."""
        
        trigger_time = trigger_time or datetime.utcnow()
        
        log_entry = {
            "log_id": f"FF-{project_id}-{trigger_time.strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "device_id": device_id,
            "trigger_time": trigger_time.isoformat(),
            "diversion_liters": diversion_liters,
            "rainfall_mm": rainfall_mm,
            "roof_area_sqm": 100,  # Would come from project data
            "diversion_efficiency": round(diversion_liters / (rainfall_mm * 100 * 0.85) * 100, 1) if rainfall_mm > 0 else 0
        }
        
        if project_id not in self.first_flush_logs:
            self.first_flush_logs[project_id] = []
        
        self.first_flush_logs[project_id].append(log_entry)
        
        logger.info(f"First flush logged for project {project_id}: {diversion_liters}L diverted")
        
        return log_entry
    
    def get_first_flush_history(
        self,
        project_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get first flush history."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        logs = [
            log for log in self.first_flush_logs.get(project_id, [])
            if datetime.fromisoformat(log["trigger_time"]) > cutoff
        ]
        
        if logs:
            total_diverted = sum(log["diversion_liters"] for log in logs)
            avg_per_event = total_diverted / len(logs)
        else:
            total_diverted = 0
            avg_per_event = 0
        
        return {
            "project_id": project_id,
            "period_days": days,
            "total_events": len(logs),
            "total_diverted_liters": round(total_diverted, 1),
            "average_per_event_liters": round(avg_per_event, 1),
            "events": logs[-10:]  # Last 10 events
        }
    
    # ==================== ALERTS ====================
    
    def get_alerts(
        self,
        project_id: int,
        alert_type: Optional[str] = None,
        unacknowledged_only: bool = True
    ) -> List[Dict]:
        """Get alerts for a project."""
        
        alerts = self.alerts.get(project_id, [])
        
        if alert_type:
            alerts = [a for a in alerts if a["alert_type"] == alert_type]
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.get("acknowledged")]
        
        return sorted(alerts, key=lambda x: x["triggered_at"], reverse=True)
    
    def acknowledge_alert(self, project_id: int, alert_id: str) -> bool:
        """Acknowledge an alert."""
        alerts = self.alerts.get(project_id, [])
        
        for alert in alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                return True
        
        return False


# Singleton instance
_iot_service: Optional[EnhancedIoTService] = None


def get_enhanced_iot_service() -> EnhancedIoTService:
    """Get or create enhanced IoT service instance."""
    global _iot_service
    if _iot_service is None:
        _iot_service = EnhancedIoTService()
    return _iot_service
