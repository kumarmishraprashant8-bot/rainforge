"""
RainForge Backend Unit Tests
============================
Tests for core API endpoints and services.

Owners: Prashant Mishra & Ishita Parmar
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_status(self):
        """Test /api/status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestQuickAssessment:
    """Test quick assessment endpoint."""
    
    def test_quick_assessment_basic(self):
        """Test basic quick assessment."""
        payload = {
            "address": "123 Test Street",
            "roof_area_sqm": 200,
            "roof_material": "concrete",
            "state": "Delhi",
            "city": "New Delhi",
            "people": 5,
            "daily_demand_liters": 200,
            "scenario": "cost_optimized"
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "runoff_potential_liters" in data
        assert "recommended_tank_size" in data
        assert "scenarios" in data
    
    def test_quick_assessment_with_coordinates(self):
        """Test quick assessment with lat/lng."""
        payload = {
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 150,
            "roof_material": "metal",
            "scenario": "max_capture"
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        assert response.status_code == 200
    
    def test_quick_assessment_all_scenarios(self):
        """Test that all 3 scenarios are returned."""
        payload = {
            "roof_area_sqm": 100,
            "roof_material": "tiles"
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        scenarios = data.get("scenarios", [])
        
        # Should have 3 scenarios
        assert len(scenarios) == 3
        scenario_names = [s["scenario"] for s in scenarios]
        assert "cost_optimized" in scenario_names
        assert "max_capture" in scenario_names
        assert "dry_season" in scenario_names


class TestMonitoring:
    """Test monitoring endpoints."""
    
    def test_get_tank_status(self):
        """Test getting tank status."""
        response = client.get("/api/v1/monitoring/1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "tank_level_percent" in data
        assert "current_volume_liters" in data
        assert data["tank_level_percent"] >= 0
        assert data["tank_level_percent"] <= 100
    
    def test_get_history(self):
        """Test getting historical data."""
        response = client.get("/api/v1/monitoring/1/history?hours=24")
        assert response.status_code == 200
        
        data = response.json()
        assert "readings" in data
        assert "period_hours" in data
        assert len(data["readings"]) > 0
    
    def test_sensor_ingestion(self):
        """Test sensor data ingestion."""
        payload = {
            "sensor_id": "SENSOR-TEST-001",
            "project_id": 1,
            "level_percent": 65.5,
            "level_volume_l": 6550,
            "battery_pct": 95.0
        }
        
        response = client.post("/api/v1/monitoring/sensor", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"


class TestBulkUpload:
    """Test bulk upload endpoints."""
    
    def test_upload_csv(self):
        """Test CSV upload."""
        csv_content = """site_id,address,lat,lng,roof_area_sqm,roof_material
SITE-TEST-001,123 Test St,28.6139,77.2090,200,concrete
SITE-TEST-002,456 Demo Ave,28.6200,77.2100,150,metal
"""
        
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = client.post("/api/bulk/upload", files=files)
        
        # Should return job ID
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["rows_total"] == 2
    
    def test_upload_empty_csv_rejected(self):
        """Test that empty CSV is rejected."""
        csv_content = "site_id,address,lat,lng\n"
        
        files = {"file": ("empty.csv", csv_content, "text/csv")}
        response = client.post("/api/bulk/upload", files=files)
        
        assert response.status_code == 400
    
    def test_get_job_status_not_found(self):
        """Test getting status of non-existent job."""
        response = client.get("/api/bulk/status/non-existent-id")
        assert response.status_code == 404


class TestCalculationEngine:
    """Test calculation engine directly."""
    
    def test_annual_yield_calculation(self):
        """Test annual yield formula."""
        from app.services.calculation_engine import CalculationEngine
        
        engine = CalculationEngine()
        annual, monthly, explanation = engine.calculate_annual_yield(
            roof_area_sqm=200,
            monthly_rainfall=[50, 30, 20, 15, 100, 200, 250, 220, 150, 80, 40, 30],
            roof_material="concrete"
        )
        
        # Verify yield is reasonable
        assert annual > 0
        assert len(monthly) == 12
        assert explanation.formula is not None
    
    def test_tank_size_optimization(self):
        """Test tank sizing."""
        from app.services.calculation_engine import CalculationEngine, Scenario
        
        engine = CalculationEngine()
        monthly_yields = [5000, 3000, 2000, 1500, 10000, 20000, 25000, 22000, 15000, 8000, 4000, 3000]
        
        size, reliability, _ = engine.optimize_tank_size(
            annual_yield_l=sum(monthly_yields),
            monthly_yields_l=monthly_yields,
            daily_demand_l=200,
            scenario=Scenario.COST_OPTIMIZED
        )
        
        assert size > 0
        assert 0 <= reliability <= 100
    
    def test_subsidy_calculation(self):
        """Test subsidy calculation for Delhi."""
        from app.services.calculation_engine import CalculationEngine
        
        engine = CalculationEngine()
        subsidy, rule, _ = engine.calculate_subsidy(
            gross_cost=100000,
            state="Delhi",
            building_type="residential"
        )
        
        # Delhi has 50% subsidy for residential
        assert subsidy > 0
        assert subsidy <= 100000


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_roof_material(self):
        """Test with invalid roof material."""
        payload = {
            "roof_area_sqm": 100,
            "roof_material": "unknown_material"
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        # Should still work with default coefficient
        assert response.status_code == 200
    
    def test_zero_roof_area(self):
        """Test with zero roof area."""
        payload = {
            "roof_area_sqm": 0,
            "roof_material": "concrete"
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_negative_coordinates(self):
        """Test with southern hemisphere coordinates."""
        payload = {
            "lat": -33.8688,  # Sydney
            "lng": 151.2093,
            "roof_area_sqm": 100
        }
        
        response = client.post("/api/assessments/quick", json=payload)
        # Should work outside India too
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
