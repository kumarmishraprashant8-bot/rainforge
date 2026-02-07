#!/usr/bin/env python3
"""
RainForge Load Testing Script
=============================
Uses Locust to test API performance under load.

Usage:
    pip install locust
    locust -f load_test.py --host=http://localhost:8000

Owners: Prashant Mishra & Ishita Parmar
"""

import json
import random
import string
from locust import HttpUser, task, between, events


class RainForgeUser(HttpUser):
    """Simulates a typical RainForge user."""
    
    wait_time = between(1, 3)  # 1-3 seconds between tasks
    
    # Sample data
    CITIES = [
        {"city": "Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
        {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
        {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
        {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
        {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    ]
    
    ROOF_MATERIALS = ["concrete", "metal", "tiles", "asphalt"]
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.project_id = random.randint(1, 100)
    
    @task(10)
    def quick_assessment(self):
        """Test quick assessment endpoint - most common operation."""
        city = random.choice(self.CITIES)
        
        payload = {
            "address": f"{random.randint(1, 500)} Demo Street",
            "lat": city["lat"] + random.uniform(-0.1, 0.1),
            "lng": city["lng"] + random.uniform(-0.1, 0.1),
            "roof_area_sqm": random.randint(50, 500),
            "roof_material": random.choice(self.ROOF_MATERIALS),
            "state": city["state"],
            "city": city["city"],
            "people": random.randint(2, 10),
            "daily_demand_liters": random.randint(100, 500),
            "scenario": random.choice(["cost_optimized", "max_capture", "dry_season"])
        }
        
        with self.client.post(
            "/api/assessments/quick",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(3)
    def get_project(self):
        """Test project retrieval."""
        with self.client.get(
            f"/api/project/{self.project_id}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:  # 404 is expected for non-existent projects
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(5)
    def monitoring_status(self):
        """Test monitoring status endpoint."""
        with self.client.get(
            f"/api/v1/monitoring/{self.project_id}/status",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                if "tank_level_percent" in data:
                    response.success()
                else:
                    response.failure("Missing tank_level_percent")
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(2)
    def monitoring_history(self):
        """Test monitoring history endpoint."""
        with self.client.get(
            f"/api/v1/monitoring/{self.project_id}/history?hours=24",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(1)
    def sensor_ingestion(self):
        """Test sensor data ingestion."""
        payload = {
            "sensor_id": f"SENSOR-{random.randint(1, 100):03d}",
            "project_id": self.project_id,
            "level_percent": random.uniform(10, 90),
            "level_volume_l": random.uniform(1000, 9000),
            "battery_pct": random.uniform(50, 100),
            "ph_level": random.uniform(6.5, 8.5),
            "turbidity_ntu": random.uniform(0, 5),
            "flow_rate_lpm": random.uniform(0, 3)
        }
        
        with self.client.post(
            "/api/v1/monitoring/sensor",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test health endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")


class BulkUploadUser(HttpUser):
    """Simulates users uploading bulk CSVs."""
    
    wait_time = between(30, 60)  # Less frequent - bulk uploads are rare
    
    @task
    def upload_small_csv(self):
        """Upload a small CSV (10 rows)."""
        csv_content = self._generate_csv(10)
        
        with self.client.post(
            "/api/bulk/upload",
            files={"file": ("test.csv", csv_content, "text/csv")},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data:
                    response.success()
                    # Could follow up with status check
                else:
                    response.failure("Missing job_id")
            else:
                response.failure(f"Status {response.status_code}")
    
    def _generate_csv(self, rows: int) -> str:
        """Generate test CSV content."""
        header = "site_id,address,lat,lng,roof_area_sqm,roof_material,state,city,people\n"
        lines = [header]
        
        for i in range(rows):
            site_id = f"SITE-{random.randint(10000, 99999)}"
            lat = 28.6 + random.uniform(-0.5, 0.5)
            lng = 77.2 + random.uniform(-0.5, 0.5)
            area = random.randint(50, 500)
            material = random.choice(["concrete", "metal", "tiles"])
            people = random.randint(2, 10)
            
            line = f"{site_id},{i} Test Street,{lat},{lng},{area},{material},Delhi,New Delhi,{people}\n"
            lines.append(line)
        
        return "".join(lines)


# Custom event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("RainForge Load Test Starting")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 60)
    print("RainForge Load Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    print("Run with: locust -f load_test.py --host=http://localhost:8000")
