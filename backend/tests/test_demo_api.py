"""
Unit Tests for RainForge Demo API
Tests for assessment, verification, and allocation endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    """Create test client."""
    # Use in-memory SQLite for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    from app.main_demo import app
    from app.models.database import init_db, SessionLocal
    from app.seed_data import seed_demo_data
    
    init_db()
    db = SessionLocal()
    seed_demo_data(db)
    db.close()
    
    with TestClient(app) as client:
        yield client


class TestAssessmentEndpoints:
    """Test /assess endpoints."""
    
    def test_create_assessment_success(self, client):
        """Test successful assessment creation."""
        response = client.post("/api/v1/assess", json={
            "site_id": "TEST-001",
            "address": "Test Address, Delhi",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 100,
            "roof_material": "concrete",
            "demand_l_per_day": 400,
            "state": "Delhi",
            "city": "New Delhi"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "assessment_id" in data
        assert data["assessment_id"].startswith("ASM-")
        assert data["site_id"] == "TEST-001"
        
        # Check 3 scenarios
        assert "scenarios" in data
        assert "cost_optimized" in data["scenarios"]
        assert "max_capture" in data["scenarios"]
        assert "dry_season" in data["scenarios"]
        
        # Check scenario structure
        for scenario in data["scenarios"].values():
            assert "tank_liters" in scenario
            assert "cost_inr" in scenario
            assert "capture_liters" in scenario
            assert "coverage_days" in scenario
            assert "roi_years" in scenario
        
        # Check subsidy
        assert data["subsidy_pct"] == 50  # Delhi subsidy
        assert data["subsidy_amount_inr"] > 0
        
        # Check PDF and verify URLs
        assert data["pdf_url"].startswith("/api/v1/assess/")
        assert data["verify_url"].startswith("/api/v1/verify/")
    
    def test_create_assessment_minimum_fields(self, client):
        """Test assessment with only required fields."""
        response = client.post("/api/v1/assess", json={
            "site_id": "TEST-MIN",
            "address": "Minimal Address",
            "lat": 19.0760,
            "lng": 72.8777,
            "roof_area_sqm": 50
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["annual_yield_liters"] > 0
    
    def test_create_assessment_invalid_area(self, client):
        """Test assessment with invalid roof area."""
        response = client.post("/api/v1/assess", json={
            "site_id": "TEST-INVALID",
            "address": "Invalid Address",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 0  # Invalid
        })
        
        assert response.status_code == 422  # Validation error


class TestMultimodalAssessment:
    """Feature A: POST /assessments with mode (address | satellite-only | photo)."""

    def test_assessments_address_mode_returns_pdf_and_confidence(self, client):
        response = client.post("/api/v1/assessments", json={
            "address": "123 Gandhi Road, New Delhi",
            "mode": "address",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 120,
            "roof_material": "concrete",
            "state": "Delhi",
            "city": "New Delhi",
        })
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        assert "confidence" in data
        assert data["confidence"] == 85.0
        assert data["assessment_id"].startswith("ASM-")
        assert "scenarios" in data

    def test_assessments_satellite_mode_returns_pdf_and_confidence(self, client):
        response = client.post("/api/v1/assessments", json={
            "address": "seeded address",
            "mode": "satellite-only",
        })
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        assert "confidence" in data
        assert data["mode"] == "satellite-only"
        assert data["confidence"] == 72.0

    def test_assessments_photo_mode_returns_pdf_and_confidence(self, client):
        response = client.post("/api/v1/assessments", json={
            "address": "Photo site",
            "mode": "photo",
        })
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        assert "confidence" in data
        assert data["mode"] == "photo"
        assert data["confidence"] == 65.0

    def test_assessments_no_mode_defaults_to_address(self, client):
        response = client.post("/api/v1/assessments", json={
            "address": "123 Demo St, Delhi",
        })
        assert response.status_code == 200
        data = response.json()
        assert "pdf_url" in data
        assert "confidence" in data
        assert data.get("mode", "address") == "address"

    def test_assessments_pdf_download_after_create(self, client):
        create = client.post("/api/v1/assessments", json={
            "address": "seeded address",
            "mode": "satellite",
        })
        assert create.status_code == 200
        pdf_url = create.json()["pdf_url"]
        get_pdf = client.get(pdf_url)
        assert get_pdf.status_code == 200
        assert get_pdf.headers.get("content-type", "").startswith("application/pdf")


class TestAssessmentRainfall:
    """Rainfall and yield tests (kept separate from multimodal)."""

    def test_rainfall_by_city(self, client):
        """Test rainfall varies by city."""
        # Mumbai (high rainfall)
        response1 = client.post("/api/v1/assess", json={
            "site_id": "TEST-MUMBAI",
            "address": "Mumbai Address",
            "lat": 19.0760,
            "lng": 72.8777,
            "roof_area_sqm": 100,
            "city": "Mumbai",
            "state": "Maharashtra"
        })
        
        # Delhi (lower rainfall)
        response2 = client.post("/api/v1/assess", json={
            "site_id": "TEST-DELHI",
            "address": "Delhi Address",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 100,
            "city": "Delhi",
            "state": "Delhi"
        })
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        mumbai_rainfall = response1.json()["annual_rainfall_mm"]
        delhi_rainfall = response2.json()["annual_rainfall_mm"]
        
        # Mumbai should have higher rainfall than Delhi
        assert mumbai_rainfall > delhi_rainfall
    
    def test_yield_calculation_deterministic(self, client):
        """Test yield calculation is deterministic."""
        payload = {
            "site_id": "TEST-DETERM",
            "address": "Test Address",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 100,
            "roof_material": "concrete",
            "city": "Delhi",
            "state": "Delhi"
        }
        
        response1 = client.post("/api/v1/assess", json=payload)
        response2 = client.post("/api/v1/assess", json=payload)
        
        assert response1.json()["annual_yield_liters"] == response2.json()["annual_yield_liters"]


class TestAuctionEndpoints:
    """Test /auction endpoints."""
    
    def test_create_auction(self, client):
        """Test auction creation."""
        # First create an assessment to get a job
        assess_response = client.post("/api/v1/assess", json={
            "site_id": "TEST-AUC",
            "address": "Auction Test",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 100
        })
        
        # Get the job ID (would need to query DB in real test)
        # For now, use a placeholder
        response = client.post("/api/v1/auction/create", json={
            "job_id": "JOB-TEST",
            "deadline_hours": 72
        })
        
        # May fail if job doesn't exist, but should not crash
        assert response.status_code in [200, 404]
    
    def test_submit_bid(self, client):
        """Test bid submission structure."""
        # Would need a real auction first
        response = client.post("/api/v1/auction/AUC-TEST/bid", json={
            "installer_id": 1,
            "price_inr": 45000,
            "timeline_days": 14,
            "warranty_months": 18
        })
        
        assert response.status_code in [200, 404]


class TestAllocationEndpoints:
    """Test /allocate endpoints."""
    
    def test_allocation_modes(self, client):
        """Test different allocation modes."""
        # Test gov_optimized mode
        response = client.post("/api/v1/allocate", json={
            "job_ids": ["JOB-TEST-001"],
            "mode": "gov_optimized"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "allocations" in data
    
    def test_allocation_equitable(self, client):
        """Test equitable allocation."""
        response = client.post("/api/v1/allocate", json={
            "job_ids": ["JOB-TEST-002"],
            "mode": "equitable"
        })
        
        assert response.status_code == 200
    
    def test_allocation_user_choice(self, client):
        """Test user choice allocation."""
        response = client.post("/api/v1/allocate", json={
            "job_ids": ["JOB-TEST-003"],
            "mode": "user_choice",
            "force_installer_id": 1
        })
        
        assert response.status_code == 200


class TestVerificationEndpoints:
    """Test /verify endpoints."""
    
    def test_verify_qr_code(self, client):
        """Test QR verification endpoint."""
        # Create an assessment first
        assess_response = client.post("/api/v1/assess", json={
            "site_id": "TEST-VERIFY",
            "address": "Verify Test",
            "lat": 28.6139,
            "lng": 77.2090,
            "roof_area_sqm": 100
        })
        
        assert assess_response.status_code == 200
        verify_url = assess_response.json()["verify_url"]
        
        # Extract verification code
        verify_code = verify_url.split("/")[-1]
        
        # Verify
        response = client.get(f"/api/v1/verify/{verify_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] == True
        assert "audit_trail" in data
    
    def test_verify_invalid_code(self, client):
        """Test verification with invalid code."""
        response = client.get("/api/v1/verify/invalid-code-12345")
        
        assert response.status_code == 404


class TestInstallerEndpoints:
    """Test installer endpoints."""
    
    def test_list_installers(self, client):
        """Test listing installers."""
        response = client.get("/api/v1/installers")
        
        assert response.status_code == 200
        data = response.json()
        assert "installers" in data
        assert len(data["installers"]) > 0
        
        # Check RPI scores
        for installer in data["installers"]:
            assert "rpi_score" in installer
            assert 0 <= installer["rpi_score"] <= 100
    
    def test_filter_by_rpi(self, client):
        """Test filtering installers by minimum RPI."""
        response = client.get("/api/v1/installers?min_rpi=80")
        
        assert response.status_code == 200
        data = response.json()
        
        for installer in data["installers"]:
            assert installer["rpi_score"] >= 80
    
    def test_installer_rpi_breakdown(self, client):
        """Test RPI breakdown for installer."""
        response = client.get("/api/v1/installers/1/rpi")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "rpi_score" in data
        assert "grade" in data
        assert "components" in data
        
        # Check component weights sum to ~1.0
        components = data["components"]
        total_weight = sum(c["weight"] for c in components.values())
        assert 0.99 <= total_weight <= 1.01


class TestMonitoringEndpoints:
    """Test /monitoring endpoints."""
    
    def test_get_telemetry(self, client):
        """Test telemetry retrieval."""
        response = client.get("/api/v1/monitoring/1?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_level" in data
        assert "statistics" in data
        assert "trend_24h" in data
        assert "alerts" in data


class TestPublicDashboard:
    """Test public dashboard endpoints."""
    
    def test_public_dashboard(self, client):
        """Test public dashboard aggregates."""
        response = client.get("/api/v1/public/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert "wards" in data
        assert "by_state" in data
    
    def test_export_csv(self, client):
        """Test CSV export."""
        response = client.get("/api/v1/public/export?format=csv")
        
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
    
    def test_export_geojson(self, client):
        """Test GeoJSON export."""
        response = client.get("/api/v1/public/export?format=geojson")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["type"] == "FeatureCollection"
        assert "features" in data


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health(self, client):
        """Test health check."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data


# Fraud Detection Tests
class TestFraudDetection:
    """Test fraud detection functionality."""
    
    def test_distance_calculation(self):
        """Test Haversine distance calculation."""
        from app.services.fraud_detector_demo import calculate_distance
        
        # Delhi to Mumbai ~1400km
        delhi = (28.6139, 77.2090)
        mumbai = (19.0760, 72.8777)
        
        distance = calculate_distance(delhi[0], delhi[1], mumbai[0], mumbai[1])
        
        # Should be approximately 1,150-1,200 km
        assert 1100000 < distance < 1250000  # meters
    
    def test_same_location_distance(self):
        """Test distance between same coordinates."""
        from app.services.fraud_detector_demo import calculate_distance
        
        distance = calculate_distance(28.6139, 77.2090, 28.6139, 77.2090)
        assert distance == 0
    
    def test_fraud_detector_clean(self):
        """Test fraud detector with clean data."""
        from app.services.fraud_detector_demo import FraudDetector
        
        detector = FraudDetector()
        
        # This would need actual photo bytes with EXIF - simplified test
        result = detector.analyze_verification(
            photos=[b"fake_photo_data"],
            submitted_lat=28.6139,
            submitted_lng=77.2090,
            site_lat=28.6139,
            site_lng=77.2090
        )
        
        assert "fraud_score" in result
        assert "flags" in result
        assert "recommendation" in result
    
    def test_fraud_detector_duplicate_hash(self):
        """Test duplicate photo detection."""
        from app.services.fraud_detector_demo import FraudDetector
        import hashlib
        
        # Create detector with known hash
        test_hash = hashlib.sha256(b"test_photo").hexdigest()
        detector = FraudDetector(known_hashes={test_hash: "VER-OLD-001"})
        
        result = detector.analyze_verification(
            photos=[b"test_photo"],  # Same content = same hash
            submitted_lat=28.6139,
            submitted_lng=77.2090,
            site_lat=28.6139,
            site_lng=77.2090
        )
        
        # Should detect reuse
        assert "photo_0_reuse_detected" in result["flags"]
        assert result["fraud_score"] >= 0.8


# RPI Calculation Tests
class TestRPICalculation:
    """Test RPI score calculation."""
    
    def test_rpi_range(self):
        """Test RPI is within 0-100 range."""
        from app.api.api_v1.endpoints.demo_api import calculate_rpi
        from app.models.database import Installer
        
        # Create mock installer
        installer = MagicMock(spec=Installer)
        installer.sla_compliance_pct = 95
        installer.capacity_available = 3
        installer.capacity_max = 10
        installer.avg_cost_factor = 1.1
        installer.jobs_completed = 50
        installer.cert_level = "certified"
        installer.warranty_months = 18
        
        rpi = calculate_rpi(installer)
        
        assert 0 <= rpi <= 100
    
    def test_rpi_premium_vs_basic(self):
        """Test premium installer has higher RPI than basic."""
        from app.api.api_v1.endpoints.demo_api import calculate_rpi
        from app.models.database import Installer
        
        # Premium installer
        premium = MagicMock(spec=Installer)
        premium.sla_compliance_pct = 95
        premium.capacity_available = 2
        premium.capacity_max = 10
        premium.avg_cost_factor = 1.0
        premium.jobs_completed = 100
        premium.cert_level = "premium"
        premium.warranty_months = 24
        
        # Basic installer
        basic = MagicMock(spec=Installer)
        basic.sla_compliance_pct = 70
        basic.capacity_available = 4
        basic.capacity_max = 5
        basic.avg_cost_factor = 1.4
        basic.jobs_completed = 10
        basic.cert_level = "basic"
        basic.warranty_months = 12
        
        premium_rpi = calculate_rpi(premium)
        basic_rpi = calculate_rpi(basic)
        
        assert premium_rpi > basic_rpi


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
