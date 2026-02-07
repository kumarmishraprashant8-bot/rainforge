#!/usr/bin/env python3
"""
RainForge Sensor Simulator
==========================
Simulates IoT sensor data for tank level monitoring.
Posts data via HTTP POST to backend API.

Usage:
    python sensor_sim.py --hours 24 --interval 300
    
Owners: Prashant Mishra & Ishita Parmar
"""

import argparse
import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests


class SensorSimulator:
    """Simulates tank level sensor with realistic patterns."""
    
    def __init__(
        self,
        sensor_id: str = "SENSOR-DEMO-001",
        project_id: int = 1,
        tank_capacity_l: float = 10000,
        initial_level_pct: float = 50.0,
        api_url: str = "http://localhost:8000"
    ):
        self.sensor_id = sensor_id
        self.project_id = project_id
        self.tank_capacity = tank_capacity_l
        self.current_level_pct = initial_level_pct
        self.battery_pct = 100.0
        self.api_url = api_url
        
        # Consumption patterns (liters per hour by hour of day)
        # Higher during morning (6-9) and evening (18-21)
        self.consumption_pattern = {
            0: 5, 1: 2, 2: 2, 3: 2, 4: 3, 5: 8,
            6: 25, 7: 40, 8: 35, 9: 20, 10: 15, 11: 15,
            12: 20, 13: 15, 14: 10, 15: 10, 16: 15, 17: 20,
            18: 35, 19: 40, 20: 30, 21: 20, 22: 15, 23: 8
        }
        
    def _simulate_consumption(self, hour: int) -> float:
        """Get consumption for given hour with randomness."""
        base = self.consumption_pattern.get(hour, 15)
        # Add ±30% randomness
        return base * random.uniform(0.7, 1.3)
    
    def _simulate_rainfall_event(self, hour: int) -> float:
        """Simulate random rainfall event."""
        # 10% chance of rain between 14:00-20:00 (monsoon pattern)
        if 14 <= hour <= 20 and random.random() < 0.1:
            # Random rainfall event: 50-500 liters added
            return random.uniform(50, 500)
        return 0
    
    def _update_battery(self, hours_elapsed: float) -> None:
        """Simulate battery drain."""
        # Assume ~0.1% per hour drain
        self.battery_pct -= 0.1 * hours_elapsed
        self.battery_pct = max(0, self.battery_pct)
    
    def generate_reading(self, timestamp: datetime = None) -> Dict[str, Any]:
        """Generate a single sensor reading."""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        hour = timestamp.hour
        
        # Simulate consumption
        consumption_l = self._simulate_consumption(hour)
        consumption_pct = (consumption_l / self.tank_capacity) * 100
        
        # Simulate rainfall
        rainfall_l = self._simulate_rainfall_event(hour)
        rainfall_pct = (rainfall_l / self.tank_capacity) * 100
        
        # Update level
        self.current_level_pct += rainfall_pct - consumption_pct
        self.current_level_pct = max(0, min(100, self.current_level_pct))
        
        # Add sensor noise (±0.5%)
        noise = random.uniform(-0.5, 0.5)
        reported_level = max(0, min(100, self.current_level_pct + noise))
        
        # Calculate volume
        volume_l = (reported_level / 100) * self.tank_capacity
        
        # pH simulation (normal range 6.5-8.5)
        ph_level = random.gauss(7.0, 0.3)
        ph_level = max(6.0, min(9.0, ph_level))
        
        # Turbidity simulation (NTU - lower is clearer)
        turbidity = random.gauss(2.0, 0.5)
        turbidity = max(0, min(10, turbidity))
        
        return {
            "sensor_id": self.sensor_id,
            "project_id": self.project_id,
            "timestamp": timestamp.isoformat(),
            "level_percent": round(reported_level, 2),
            "level_volume_l": round(volume_l, 1),
            "battery_pct": round(self.battery_pct, 1),
            "ph_level": round(ph_level, 2),
            "turbidity_ntu": round(turbidity, 2),
            "flow_rate_lpm": round(consumption_l / 60, 2) if consumption_l > 0 else 0,
            "raw_data": {
                "consumption_l": round(consumption_l, 1),
                "rainfall_l": round(rainfall_l, 1),
                "noise_applied": round(noise, 3)
            }
        }
    
    def post_reading(self, reading: Dict[str, Any]) -> bool:
        """Post reading to API."""
        try:
            response = requests.post(
                f"{self.api_url}/api/monitoring/sensor",
                json=reading,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Failed to post: {e}")
            return False
    
    def run_simulation(
        self,
        hours: int = 24,
        interval_seconds: int = 300,
        realtime: bool = False,
        dry_run: bool = False
    ) -> list:
        """
        Run continuous simulation.
        
        Args:
            hours: Number of hours to simulate
            interval_seconds: Seconds between readings
            realtime: If True, wait actual interval between readings
            dry_run: If True, don't post to API
        
        Returns:
            List of all generated readings
        """
        readings = []
        readings_per_hour = 3600 // interval_seconds
        total_readings = hours * readings_per_hour
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        print(f"Starting simulation: {total_readings} readings over {hours} hours")
        print(f"Sensor: {self.sensor_id}, Tank: {self.tank_capacity}L")
        print("-" * 60)
        
        for i in range(total_readings):
            # Calculate timestamp
            if realtime:
                timestamp = datetime.now()
                self._update_battery(interval_seconds / 3600)
            else:
                timestamp = start_time + timedelta(seconds=i * interval_seconds)
                self._update_battery(interval_seconds / 3600)
            
            # Generate reading
            reading = self.generate_reading(timestamp)
            readings.append(reading)
            
            # Print progress
            if i % 10 == 0:
                print(f"[{timestamp.strftime('%H:%M')}] Level: {reading['level_percent']:.1f}% "
                      f"({reading['level_volume_l']:.0f}L), Battery: {reading['battery_pct']:.0f}%")
            
            # Post to API
            if not dry_run:
                success = self.post_reading(reading)
                if not success and i == 0:
                    print("Warning: Failed to connect to API. Continuing in dry-run mode.")
                    dry_run = True
            
            # Wait if realtime mode
            if realtime:
                time.sleep(interval_seconds)
        
        print("-" * 60)
        print(f"Simulation complete. Generated {len(readings)} readings.")
        
        return readings


def main():
    parser = argparse.ArgumentParser(description="RainForge Sensor Simulator")
    parser.add_argument("--hours", type=int, default=24, help="Hours to simulate")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between readings")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Backend API URL")
    parser.add_argument("--sensor-id", default="SENSOR-DEMO-001", help="Sensor ID")
    parser.add_argument("--project-id", type=int, default=1, help="Project ID")
    parser.add_argument("--tank-capacity", type=float, default=10000, help="Tank capacity in liters")
    parser.add_argument("--initial-level", type=float, default=60, help="Initial level percentage")
    parser.add_argument("--realtime", action="store_true", help="Run in real-time mode")
    parser.add_argument("--dry-run", action="store_true", help="Don't post to API")
    parser.add_argument("--output", help="Save readings to JSON file")
    
    args = parser.parse_args()
    
    simulator = SensorSimulator(
        sensor_id=args.sensor_id,
        project_id=args.project_id,
        tank_capacity_l=args.tank_capacity,
        initial_level_pct=args.initial_level,
        api_url=args.api_url
    )
    
    readings = simulator.run_simulation(
        hours=args.hours,
        interval_seconds=args.interval,
        realtime=args.realtime,
        dry_run=args.dry_run
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(readings, f, indent=2)
        print(f"Saved readings to {args.output}")


if __name__ == "__main__":
    main()
