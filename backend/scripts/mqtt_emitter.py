"""
Mock MQTT Emitter for RainForge Demo
Simulates IoT sensor data for tank monitoring
"""

import json
import random
import time
from datetime import datetime, timezone
import argparse


def generate_tank_reading(device_id: str, current_level: float, tank_capacity: int = 5000) -> dict:
    """Generate a tank level reading."""
    return {
        "device_id": device_id,
        "sensor_type": "tank_level",
        "value": round(current_level, 1),
        "unit": "liters",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_pct": round(random.uniform(85, 100), 1),
        "signal_rssi": random.randint(-60, -30)
    }


def generate_flow_reading(device_id: str, flow_rate: float) -> dict:
    """Generate a flow meter reading."""
    return {
        "device_id": device_id,
        "sensor_type": "flow_meter",
        "value": round(flow_rate, 2),
        "unit": "liters",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_pct": round(random.uniform(85, 100), 1),
        "signal_rssi": random.randint(-60, -30)
    }


def generate_quality_reading(device_id: str) -> dict:
    """Generate water quality reading."""
    return {
        "device_id": device_id,
        "sensor_type": "water_quality",
        "value": round(random.uniform(6.5, 7.5), 2),  # pH
        "unit": "pH",
        "tds": random.randint(100, 200),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_pct": round(random.uniform(85, 100), 1),
        "signal_rssi": random.randint(-60, -30)
    }


def simulate_device(device_id: str, project_id: int, tank_capacity: int = 5000):
    """Simulate a single device sending telemetry."""
    current_level = random.uniform(2000, 4000)
    hour = datetime.now().hour
    
    while True:
        hour = datetime.now().hour
        
        # Simulate usage patterns
        if 6 <= hour <= 9:  # Morning usage
            change = random.uniform(-50, -150)  # More usage
        elif 18 <= hour <= 21:  # Evening usage
            change = random.uniform(-30, -100)
        elif 14 <= hour <= 17:  # Afternoon rain chance
            if random.random() > 0.7:
                change = random.uniform(100, 500)  # Rain collection
            else:
                change = random.uniform(-20, -50)
        else:
            change = random.uniform(-20, -40)  # Low usage
        
        current_level = max(100, min(tank_capacity * 0.95, current_level + change))
        
        # Tank level reading
        reading = generate_tank_reading(device_id, current_level, tank_capacity)
        reading["project_id"] = project_id
        
        print(json.dumps(reading))
        
        # Flow reading during usage hours
        if change < 0:
            flow = generate_flow_reading(device_id, abs(change))
            flow["project_id"] = project_id
            print(json.dumps(flow))
        
        # Periodic quality check
        if random.random() > 0.9:
            quality = generate_quality_reading(device_id)
            quality["project_id"] = project_id
            print(json.dumps(quality))
        
        # Alert for high/low levels
        if current_level > tank_capacity * 0.9:
            print(json.dumps({
                "device_id": device_id,
                "project_id": project_id,
                "alert_type": "overflow_warning",
                "message": f"Tank level at {round(current_level/tank_capacity*100, 1)}%",
                "severity": "warning",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
        elif current_level < tank_capacity * 0.1:
            print(json.dumps({
                "device_id": device_id,
                "project_id": project_id,
                "alert_type": "low_level",
                "message": f"Tank level at {round(current_level/tank_capacity*100, 1)}%",
                "severity": "critical",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
        
        time.sleep(60)  # Reading every minute


def main():
    parser = argparse.ArgumentParser(description="Mock MQTT emitter for RainForge demo")
    parser.add_argument("--device-id", default="DEV-001", help="Device ID")
    parser.add_argument("--project-id", type=int, default=1, help="Project ID")
    parser.add_argument("--tank-capacity", type=int, default=5000, help="Tank capacity in liters")
    parser.add_argument("--interval", type=int, default=60, help="Reading interval in seconds")
    
    args = parser.parse_args()
    
    print(f"🌧️ RainForge MQTT Emitter Started")
    print(f"   Device: {args.device_id}")
    print(f"   Project: {args.project_id}")
    print(f"   Tank Capacity: {args.tank_capacity}L")
    print(f"   Interval: {args.interval}s")
    print("-" * 40)
    
    try:
        simulate_device(args.device_id, args.project_id, args.tank_capacity)
    except KeyboardInterrupt:
        print("\n👋 Emitter stopped")


if __name__ == "__main__":
    main()
