"""Telemetry ingestion service for IoT sensor data."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

from app.services.mqtt_client import SensorReading, get_mqtt_client

logger = logging.getLogger(__name__)


@dataclass
class TelemetryStats:
    """Aggregated telemetry statistics."""
    project_id: int
    sensor_type: str
    avg_value: float
    min_value: float
    max_value: float
    reading_count: int
    last_reading: datetime
    period_hours: int


class TelemetryService:
    """
    Service for ingesting and querying IoT telemetry data.
    In production, this would write to TimescaleDB.
    """
    
    # In-memory storage for demo (replace with TimescaleDB)
    _readings: List[Dict[str, Any]] = []
    _max_readings = 100000  # Limit for demo
    
    @classmethod
    def ingest_reading(cls, reading: SensorReading) -> bool:
        """
        Store a sensor reading.
        In production: INSERT INTO sensor_readings using asyncpg.
        """
        try:
            record = {
                "time": reading.timestamp,
                "device_id": reading.device_id,
                "project_id": reading.project_id,
                "sensor_type": reading.sensor_type,
                "value": reading.value,
                "unit": reading.unit,
                "battery_percent": reading.battery_percent,
                "signal_strength": reading.signal_strength
            }
            
            cls._readings.append(record)
            
            # Trim old readings if limit exceeded
            if len(cls._readings) > cls._max_readings:
                cls._readings = cls._readings[-cls._max_readings:]
            
            logger.debug(
                f"Ingested: project={reading.project_id}, "
                f"sensor={reading.sensor_type}, value={reading.value}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest reading: {e}")
            return False
    
    @classmethod
    def get_latest_reading(
        cls, 
        project_id: int, 
        sensor_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent reading for a sensor."""
        matching = [
            r for r in reversed(cls._readings)
            if r["project_id"] == project_id and r["sensor_type"] == sensor_type
        ]
        return matching[0] if matching else None
    
    @classmethod
    def get_readings(
        cls,
        project_id: int,
        sensor_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get historical readings for a project.
        In production: SELECT from TimescaleDB with time_bucket.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        readings = [
            r for r in cls._readings
            if r["project_id"] == project_id
            and r["time"] >= cutoff
            and (sensor_type is None or r["sensor_type"] == sensor_type)
        ]
        
        # Sort by time and limit
        readings.sort(key=lambda x: x["time"], reverse=True)
        return readings[:limit]
    
    @classmethod
    def get_stats(
        cls,
        project_id: int,
        sensor_type: str,
        hours: int = 24
    ) -> Optional[TelemetryStats]:
        """
        Get aggregated statistics for a sensor.
        In production: Use TimescaleDB continuous aggregates.
        """
        readings = cls.get_readings(project_id, sensor_type, hours)
        
        if not readings:
            return None
        
        values = [r["value"] for r in readings]
        
        return TelemetryStats(
            project_id=project_id,
            sensor_type=sensor_type,
            avg_value=sum(values) / len(values),
            min_value=min(values),
            max_value=max(values),
            reading_count=len(readings),
            last_reading=readings[0]["time"],
            period_hours=hours
        )
    
    @classmethod
    def get_project_dashboard(cls, project_id: int) -> Dict[str, Any]:
        """Get dashboard data for a project's IoT sensors."""
        sensor_types = ["tank_level", "flow_rate", "rainfall", "temperature"]
        
        dashboard = {
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sensors": {}
        }
        
        for sensor_type in sensor_types:
            latest = cls.get_latest_reading(project_id, sensor_type)
            stats = cls.get_stats(project_id, sensor_type, hours=24)
            
            dashboard["sensors"][sensor_type] = {
                "current": latest["value"] if latest else None,
                "unit": latest["unit"] if latest else None,
                "last_updated": latest["time"].isoformat() if latest else None,
                "stats_24h": {
                    "avg": round(stats.avg_value, 2) if stats else None,
                    "min": round(stats.min_value, 2) if stats else None,
                    "max": round(stats.max_value, 2) if stats else None,
                    "count": stats.reading_count if stats else 0
                }
            }
        
        return dashboard
    
    @classmethod
    def start_ingestion(cls):
        """Start the MQTT message ingestion."""
        mqtt_client = get_mqtt_client()
        mqtt_client.set_message_handler(cls.ingest_reading)
        
        if mqtt_client.connect():
            logger.info("🚀 Telemetry ingestion started")
        else:
            logger.warning("⚠️ MQTT not available, using simulated data")
    
    @classmethod
    def get_reading_count(cls) -> int:
        """Get total number of stored readings."""
        return len(cls._readings)
    
    @classmethod
    def clear_readings(cls):
        """Clear all readings (for testing)."""
        cls._readings = []


# SQL for TimescaleDB (production)
TIMESCALE_SCHEMA = """
-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Main readings table
CREATE TABLE IF NOT EXISTS sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    project_id INTEGER NOT NULL,
    sensor_type VARCHAR(30) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(10),
    battery_percent INTEGER,
    signal_strength INTEGER,
    PRIMARY KEY (time, device_id)
);

-- Convert to hypertable
SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_readings_project ON sensor_readings (project_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_readings_type ON sensor_readings (sensor_type, time DESC);

-- Retention policy: 90 days
SELECT add_retention_policy('sensor_readings', INTERVAL '90 days', if_not_exists => TRUE);

-- Continuous aggregate for hourly stats
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_sensor_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    project_id,
    sensor_type,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as reading_count
FROM sensor_readings
GROUP BY bucket, project_id, sensor_type
WITH NO DATA;

-- Refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('hourly_sensor_stats',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Daily stats view
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_sensor_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    project_id,
    sensor_type,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as reading_count
FROM sensor_readings
GROUP BY bucket, project_id, sensor_type
WITH NO DATA;
"""
