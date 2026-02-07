"""
Seed Data for RainForge Demo
Populates database with demo installers, sites, telemetry, etc.
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.database import (
    Installer, Assessment, Telemetry, SubsidyRule, Ward,
    AssessmentStatus
)


def seed_demo_data(db: Session):
    """Seed all demo data if database is empty."""
    
    # Check if already seeded
    if db.query(Installer).count() > 0:
        print("📦 Demo data already seeded")
        return
    
    print("🌱 Seeding demo data...")
    
    seed_installers(db)
    seed_subsidy_rules(db)
    seed_sample_assessments(db)
    seed_telemetry(db)
    seed_wards(db)
    
    db.commit()
    print("✅ Demo data seeded successfully!")


def seed_installers(db: Session):
    """Seed installer data."""
    installers = [
        {
            "name": "Ramesh Kumar",
            "company": "AquaTech Solutions",
            "email": "ramesh@aquatech.in",
            "phone": "+91-9876543210",
            "lat": 28.6139,
            "lng": 77.2090,
            "rpi_score": 92.5,
            "capacity_available": 5,
            "capacity_max": 10,
            "avg_cost_factor": 1.0,
            "sla_compliance_pct": 96.0,
            "jobs_completed": 145,
            "cert_level": "premium",
            "service_areas": "Delhi,Noida,Gurgaon",
            "warranty_months": 24,
            "specialization": "residential"
        },
        {
            "name": "Priya Sharma",
            "company": "GreenWater Systems",
            "email": "priya@greenwater.in",
            "phone": "+91-9876543211",
            "lat": 28.4595,
            "lng": 77.0266,
            "rpi_score": 78.3,
            "capacity_available": 3,
            "capacity_max": 8,
            "avg_cost_factor": 1.15,
            "sla_compliance_pct": 88.5,
            "jobs_completed": 67,
            "cert_level": "certified",
            "service_areas": "Gurgaon,Faridabad",
            "warranty_months": 18,
            "specialization": "commercial"
        },
        {
            "name": "Mohammed Ali",
            "company": "EcoRain Pvt Ltd",
            "email": "mali@ecorain.in",
            "phone": "+91-9876543212",
            "lat": 19.0760,
            "lng": 72.8777,
            "rpi_score": 85.1,
            "capacity_available": 7,
            "capacity_max": 15,
            "avg_cost_factor": 0.95,
            "sla_compliance_pct": 92.0,
            "jobs_completed": 203,
            "cert_level": "premium",
            "service_areas": "Mumbai,Thane,Navi Mumbai",
            "warranty_months": 24,
            "specialization": "all"
        },
        {
            "name": "Suresh Reddy",
            "company": "JalSeva Enterprises",
            "email": "suresh@jalseva.in",
            "phone": "+91-9876543213",
            "lat": 12.9716,
            "lng": 77.5946,
            "rpi_score": 61.2,
            "capacity_available": 2,
            "capacity_max": 5,
            "avg_cost_factor": 1.25,
            "sla_compliance_pct": 75.0,
            "jobs_completed": 28,
            "cert_level": "basic",
            "service_areas": "Bangalore,Mysore",
            "warranty_months": 12,
            "specialization": "residential"
        },
        {
            "name": "Lakshmi Devi",
            "company": "RainHarvest Co",
            "email": "lakshmi@rainharvest.in",
            "phone": "+91-9876543214",
            "lat": 17.3850,
            "lng": 78.4867,
            "rpi_score": 88.7,
            "capacity_available": 4,
            "capacity_max": 10,
            "avg_cost_factor": 1.05,
            "sla_compliance_pct": 94.5,
            "jobs_completed": 112,
            "cert_level": "certified",
            "service_areas": "Hyderabad,Secunderabad",
            "warranty_months": 18,
            "specialization": "all"
        },
        {
            "name": "Vikram Singh",
            "company": "AquaSave India",
            "email": "vikram@aquasave.in",
            "phone": "+91-9876543215",
            "lat": 13.0827,
            "lng": 80.2707,
            "rpi_score": 45.8,
            "capacity_available": 1,
            "capacity_max": 3,
            "avg_cost_factor": 1.40,
            "sla_compliance_pct": 65.0,
            "jobs_completed": 12,
            "cert_level": "basic",
            "service_areas": "Chennai,Kanchipuram",
            "warranty_months": 12,
            "specialization": "residential"
        }
    ]
    
    for data in installers:
        installer = Installer(**data)
        db.add(installer)
    
    print(f"  📋 Added {len(installers)} installers")


def seed_subsidy_rules(db: Session):
    """Seed state subsidy rules."""
    rules = [
        {
            "state_code": "DL",
            "state_name": "Delhi",
            "scheme_name": "Delhi Jal Board RWH Scheme",
            "subsidy_pct": 50,
            "max_subsidy_inr": 50000,
            "eligible_building_types": "residential,commercial,government",
            "min_roof_sqm": 50,
            "max_roof_sqm": 5000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://delhijalboard.nic.in"
        },
        {
            "state_code": "MH",
            "state_name": "Maharashtra",
            "scheme_name": "Maharashtra RWH Rebate",
            "subsidy_pct": 35,
            "max_subsidy_inr": 75000,
            "eligible_building_types": "residential,commercial",
            "min_roof_sqm": 100,
            "max_roof_sqm": 10000,
            "valid_from": datetime(2024, 4, 1),
            "valid_until": datetime(2025, 3, 31),
            "source_url": "https://mahawater.gov.in"
        },
        {
            "state_code": "KA",
            "state_name": "Karnataka",
            "scheme_name": "Bangaluru Jalasiri",
            "subsidy_pct": 40,
            "max_subsidy_inr": 40000,
            "eligible_building_types": "residential",
            "min_roof_sqm": 50,
            "max_roof_sqm": 2000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://bwssb.gov.in"
        },
        {
            "state_code": "TN",
            "state_name": "Tamil Nadu",
            "scheme_name": "TN RWH Mandate",
            "subsidy_pct": 30,
            "max_subsidy_inr": 35000,
            "eligible_building_types": "residential,commercial,government",
            "min_roof_sqm": 100,
            "max_roof_sqm": 5000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://tnpwd.gov.in"
        },
        {
            "state_code": "TS",
            "state_name": "Telangana",
            "scheme_name": "HMWSSB Green Building",
            "subsidy_pct": 45,
            "max_subsidy_inr": 60000,
            "eligible_building_types": "residential,commercial",
            "min_roof_sqm": 75,
            "max_roof_sqm": 3000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://hyderabadwater.gov.in"
        },
        {
            "state_code": "RJ",
            "state_name": "Rajasthan",
            "scheme_name": "Mukhyamantri Jal Swavlamban",
            "subsidy_pct": 60,
            "max_subsidy_inr": 100000,
            "eligible_building_types": "residential,government",
            "min_roof_sqm": 50,
            "max_roof_sqm": 10000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://water.rajasthan.gov.in"
        },
        {
            "state_code": "GA",
            "state_name": "Goa",
            "scheme_name": "Goa RWH Incentive",
            "subsidy_pct": 50,
            "max_subsidy_inr": 50000,
            "eligible_building_types": "residential,commercial",
            "min_roof_sqm": 50,
            "max_roof_sqm": 2000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://goawater.gov.in"
        },
        {
            "state_code": "KL",
            "state_name": "Kerala",
            "scheme_name": "Kerala RWH Mission",
            "subsidy_pct": 50,
            "max_subsidy_inr": 75000,
            "eligible_building_types": "residential,commercial",
            "min_roof_sqm": 50,
            "max_roof_sqm": 5000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://kwa.kerala.gov.in"
        },
        {
            "state_code": "GJ",
            "state_name": "Gujarat",
            "scheme_name": "Gujarat RWH Policy",
            "subsidy_pct": 40,
            "max_subsidy_inr": 50000,
            "eligible_building_types": "residential,commercial,industrial",
            "min_roof_sqm": 100,
            "max_roof_sqm": 5000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://gwssb.gujarat.gov.in"
        },
        {
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "scheme_name": "UP RWH Incentive",
            "subsidy_pct": 25,
            "max_subsidy_inr": 25000,
            "eligible_building_types": "residential",
            "min_roof_sqm": 100,
            "max_roof_sqm": 2000,
            "valid_from": datetime(2024, 1, 1),
            "valid_until": datetime(2025, 12, 31),
            "source_url": "https://upjn.org"
        }
    ]
    
    for data in rules:
        rule = SubsidyRule(**data)
        db.add(rule)
    
    print(f"  📋 Added {len(rules)} subsidy rules")


def seed_sample_assessments(db: Session):
    """Seed sample assessment data."""
    import uuid
    
    assessments = [
        {
            "assessment_id": "ASM-20260203-DEMO01",
            "site_id": "SITE-DEMO-001",
            "address": "15 Janpath Road, New Delhi",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 150,
            "roof_material": "concrete",
            "demand_l_per_day": 500,
            "floors": 2,
            "people": 5,
            "state": "Delhi",
            "city": "New Delhi",
            "scenarios": {
                "cost_optimized": {"name": "Cost Optimized", "tank_liters": 3000, "cost_inr": 28000, "capture_liters": 53550, "coverage_days": 6, "roi_years": 6.2},
                "max_capture": {"name": "Maximum Capture", "tank_liters": 8000, "cost_inr": 52000, "capture_liters": 84788, "coverage_days": 16, "roi_years": 7.8},
                "dry_season": {"name": "Dry Season", "tank_liters": 5000, "cost_inr": 38000, "capture_liters": 66919, "coverage_days": 10, "roi_years": 7.0}
            },
            "annual_rainfall_mm": 700,
            "annual_yield_liters": 89250,
            "recommended_tank_liters": 8000,
            "total_cost_inr": 52000,
            "subsidy_pct": 50,
            "subsidy_amount_inr": 26000,
            "net_cost_inr": 26000,
            "roi_years": 7.8,
            "co2_avoided_kg": 22.76,
            "status": AssessmentStatus.PDF_GENERATED,
            "qr_verification_code": str(uuid.uuid4())
        }
    ]
    
    for data in assessments:
        assessment = Assessment(**data)
        db.add(assessment)
    
    print(f"  📋 Added {len(assessments)} sample assessments")


def seed_telemetry(db: Session):
    """Seed IoT telemetry data."""
    from datetime import timezone
    
    base_time = datetime.now(timezone.utc) - timedelta(hours=24)
    project_ids = [1, 2, 3]
    
    readings = []
    for project_id in project_ids:
        tank_capacity = 5000
        current_level = 3500 + (project_id * 200)  # Different starting points
        
        for hour in range(24):
            timestamp = base_time + timedelta(hours=hour)
            
            # Simulate tank level changes
            if 6 <= hour <= 9:  # Morning usage
                current_level -= 150
            elif 18 <= hour <= 21:  # Evening usage
                current_level -= 120
            elif 14 <= hour <= 16:  # Afternoon rain
                current_level += 300
            
            current_level = max(500, min(tank_capacity, current_level))
            
            readings.append({
                "project_id": project_id,
                "device_id": f"DEV-{project_id:03d}",
                "timestamp": timestamp.replace(tzinfo=None),
                "sensor_type": "tank_level",
                "value": current_level,
                "unit": "liters",
                "battery_pct": 95 - (hour * 0.1),
                "signal_rssi": -45 - (hour % 10)
            })
            
            # Add flow readings for some hours
            if hour in [7, 8, 18, 19]:
                readings.append({
                    "project_id": project_id,
                    "device_id": f"DEV-{project_id:03d}",
                    "timestamp": timestamp.replace(tzinfo=None),
                    "sensor_type": "flow_meter",
                    "value": 50 + (hour * 5),
                    "unit": "liters",
                    "battery_pct": 95 - (hour * 0.1),
                    "signal_rssi": -45 - (hour % 10)
                })
    
    for data in readings:
        telemetry = Telemetry(**data)
        db.add(telemetry)
    
    print(f"  📋 Added {len(readings)} telemetry readings")


def seed_wards(db: Session):
    """Seed ward boundary data."""
    wards = [
        {
            "ward_id": "WARD-DL-001",
            "ward_name": "Connaught Place",
            "city": "New Delhi",
            "state": "Delhi",
            "population": 45000,
            "area_sqkm": 2.8,
            "geojson": {
                "type": "Polygon",
                "coordinates": [[[77.209, 77.225], [77.225, 28.62], [77.225, 28.605], [77.209, 28.605], [77.209, 28.62]]]
            },
            "total_projects": 15,
            "verified_projects": 12,
            "total_capture_liters": 1250000,
            "total_investment_inr": 650000
        },
        {
            "ward_id": "WARD-DL-002",
            "ward_name": "Sector 5 Gurugram",
            "city": "Gurugram",
            "state": "Delhi",
            "population": 32000,
            "area_sqkm": 4.2,
            "geojson": {
                "type": "Polygon",
                "coordinates": [[[77.02, 28.465], [77.04, 28.465], [77.04, 28.45], [77.02, 28.45], [77.02, 28.465]]]
            },
            "total_projects": 8,
            "verified_projects": 6,
            "total_capture_liters": 820000,
            "total_investment_inr": 420000
        },
        {
            "ward_id": "WARD-KA-001",
            "ward_name": "Koramangala",
            "city": "Bangalore",
            "state": "Karnataka",
            "population": 68000,
            "area_sqkm": 5.1,
            "geojson": {
                "type": "Polygon",
                "coordinates": [[[77.615, 12.935], [77.64, 12.935], [77.64, 12.91], [77.615, 12.91], [77.615, 12.935]]]
            },
            "total_projects": 22,
            "verified_projects": 18,
            "total_capture_liters": 2100000,
            "total_investment_inr": 980000
        }
    ]
    
    for data in wards:
        ward = Ward(**data)
        db.add(ward)
    
    print(f"  📋 Added {len(wards)} wards")


# Also create CSV files for reference
def export_seed_data_to_csv():
    """Export seed data to CSV files (for README reference)."""
    os.makedirs("seed_data", exist_ok=True)
    
    # Installers CSV
    with open("seed_data/seed_installers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "company", "lat", "lng", "rpi_score", "capacity_available", "capacity_max", "cert_level", "service_areas"])
        writer.writerow([1, "Ramesh Kumar", "AquaTech Solutions", 28.6139, 77.2090, 92.5, 5, 10, "premium", "Delhi,Noida,Gurgaon"])
        writer.writerow([2, "Priya Sharma", "GreenWater Systems", 28.4595, 77.0266, 78.3, 3, 8, "certified", "Gurgaon,Faridabad"])
        writer.writerow([3, "Mohammed Ali", "EcoRain Pvt Ltd", 19.0760, 72.8777, 85.1, 7, 15, "premium", "Mumbai,Thane"])
        writer.writerow([4, "Suresh Reddy", "JalSeva Enterprises", 12.9716, 77.5946, 61.2, 2, 5, "basic", "Bangalore,Mysore"])
        writer.writerow([5, "Lakshmi Devi", "RainHarvest Co", 17.3850, 78.4867, 88.7, 4, 10, "certified", "Hyderabad"])
        writer.writerow([6, "Vikram Singh", "AquaSave India", 13.0827, 80.2707, 45.8, 1, 3, "basic", "Chennai"])
    
    # Subsidy rules CSV
    with open("seed_data/subsidy_rules.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["state_code", "state_name", "subsidy_pct", "max_subsidy_inr", "eligible_types"])
        writer.writerow(["DL", "Delhi", 50, 50000, "residential,commercial"])
        writer.writerow(["MH", "Maharashtra", 35, 75000, "residential,commercial"])
        writer.writerow(["KA", "Karnataka", 40, 40000, "residential"])
        writer.writerow(["TN", "Tamil Nadu", 30, 35000, "residential,commercial"])
        writer.writerow(["TS", "Telangana", 45, 60000, "residential,commercial"])
        writer.writerow(["RJ", "Rajasthan", 60, 100000, "residential,government"])
        writer.writerow(["GA", "Goa", 50, 50000, "residential,commercial"])
        writer.writerow(["KL", "Kerala", 50, 75000, "residential,commercial"])
        writer.writerow(["GJ", "Gujarat", 40, 50000, "residential,commercial,industrial"])
        writer.writerow(["UP", "Uttar Pradesh", 25, 25000, "residential"])
    
    print("📁 CSV seed data exported to seed_data/")
