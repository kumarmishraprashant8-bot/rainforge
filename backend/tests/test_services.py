"""
RainForge Unit Tests
Comprehensive test suite for backend services
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import json


# ==================== PDF GENERATOR TESTS ====================

class TestPDFGenerator:
    """Tests for PDF generation service."""
    
    def test_assessment_report_generation(self):
        """Test assessment report PDF generation."""
        from app.services.pdf_generator import get_pdf_generator
        
        generator = get_pdf_generator()
        
        pdf_bytes = generator.generate_assessment_report(
            project_name="Test Project",
            address="123 Test Street",
            roof_area_sqm=100,
            annual_rainfall_mm=800,
            runoff_coefficient=0.85,
            yearly_yield_liters=68000,
            recommended_tank_liters=5000,
            estimated_cost_min=40000,
            estimated_cost_max=60000,
            roi_years=3.5,
            carbon_offset_kg=50,
            recommendations=[]
        )
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # Check PDF magic bytes
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_certificate_generation(self):
        """Test certificate PDF generation."""
        from app.services.pdf_generator import get_pdf_generator
        
        generator = get_pdf_generator()
        
        pdf_bytes = generator.generate_certificate(
            project_id=123,
            project_name="Test Project",
            owner_name="John Doe",
            address="123 Test Street",
            tank_capacity=5000,
            installation_date="01-01-2024",
            installer_name="Test Installer",
            verification_date="05-01-2024",
            certificate_number="RF-2024-000123"
        )
        
        assert pdf_bytes is not None
        assert pdf_bytes[:4] == b'%PDF'


# ==================== QR GENERATOR TESTS ====================

class TestQRGenerator:
    """Tests for QR code generation."""
    
    def test_project_qr_generation(self):
        """Test project QR code generation."""
        from app.services.qr_generator import get_qr_generator
        
        generator = get_qr_generator()
        qr = generator.generate_project_qr(123)
        
        assert qr.content == "https://rainforge.gov.in/project/123"
        assert qr.raw_bytes is not None
        assert qr.data_url.startswith("data:image/")
    
    def test_payment_qr_generation(self):
        """Test UPI payment QR generation."""
        from app.services.qr_generator import get_qr_generator
        
        generator = get_qr_generator()
        qr = generator.generate_payment_qr(
            upi_id="test@upi",
            amount=1000.00,
            project_id=123
        )
        
        assert "upi://pay" in qr.content
        assert "1000.00" in qr.content


# ==================== RATE LIMITER TESTS ====================

class TestRateLimiter:
    """Tests for rate limiting."""
    
    def test_rate_limit_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        from app.services.rate_limiter import get_rate_limiter, RateLimitConfig
        
        limiter = get_rate_limiter()
        
        # Reset limiter
        limiter._requests.clear()
        
        config = RateLimitConfig(requests=5, window=60)
        
        for i in range(5):
            allowed, info = limiter.check("test_user", "/test", config)
            assert allowed is True
            assert info["remaining"] >= 0
    
    def test_rate_limit_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        from app.services.rate_limiter import get_rate_limiter, RateLimitConfig
        
        limiter = get_rate_limiter()
        limiter._requests.clear()
        
        config = RateLimitConfig(requests=3, window=60)
        
        # Use up the limit
        for i in range(3):
            limiter.check("test_user_2", "/test2", config)
        
        # This should be blocked
        allowed, info = limiter.check("test_user_2", "/test2", config)
        assert allowed is False
        assert info["remaining"] == 0


# ==================== GAMIFICATION TESTS ====================

class TestGamification:
    """Tests for gamification service."""
    
    @pytest.mark.asyncio
    async def test_add_points(self):
        """Test adding points to user."""
        from app.services.gamification import get_gamification_service
        
        service = get_gamification_service()
        
        total = await service.add_points("test_user", 100, "test")
        assert total >= 100
    
    @pytest.mark.asyncio
    async def test_get_user_level(self):
        """Test user level calculation."""
        from app.services.gamification import get_gamification_service
        
        service = get_gamification_service()
        service._user_points["level_test"] = 1500
        
        level = service.get_user_level("level_test")
        
        assert "level" in level
        assert "points" in level
        assert level["points"] == 1500
    
    @pytest.mark.asyncio
    async def test_installer_leaderboard(self):
        """Test installer leaderboard generation."""
        from app.services.gamification import get_gamification_service
        
        service = get_gamification_service()
        
        leaderboard = await service.get_installer_leaderboard(limit=5)
        
        assert len(leaderboard) == 5
        assert all(e.rank > 0 for e in leaderboard)


# ==================== MAINTENANCE CALENDAR TESTS ====================

class TestMaintenanceCalendar:
    """Tests for maintenance calendar."""
    
    def test_schedule_generation(self):
        """Test maintenance schedule generation."""
        from app.services.maintenance_calendar import get_calendar_service
        
        service = get_calendar_service()
        
        events = service.generate_maintenance_schedule(
            project_id=1,
            project_name="Test Project",
            installation_date=datetime.now() - timedelta(days=30),
            years_ahead=1
        )
        
        assert len(events) > 0
        assert all(e.project_id == 1 for e in events)
    
    def test_ical_export(self):
        """Test iCal export."""
        from app.services.maintenance_calendar import get_calendar_service
        
        service = get_calendar_service()
        
        events = service.generate_maintenance_schedule(
            project_id=1,
            project_name="Test",
            installation_date=datetime.now() - timedelta(days=30)
        )
        
        ical = service.export_to_ical(events)
        
        assert "BEGIN:VCALENDAR" in ical
        assert "END:VCALENDAR" in ical


# ==================== DATA EXPORT TESTS ====================

class TestDataExport:
    """Tests for data export."""
    
    def test_csv_export(self):
        """Test CSV export."""
        from app.services.data_export import get_export_service
        
        service = get_export_service()
        
        data = [
            {"id": 1, "name": "Project 1", "city": "Mumbai"},
            {"id": 2, "name": "Project 2", "city": "Delhi"}
        ]
        
        result = service.export_projects(data, "csv")
        
        assert result.content_type == "text/csv"
        assert result.record_count == 2
        assert b"id" in result.data
    
    def test_json_export(self):
        """Test JSON export."""
        from app.services.data_export import get_export_service
        
        service = get_export_service()
        
        data = [{"id": 1, "name": "Test"}]
        result = service.export_projects(data, "json")
        
        assert result.content_type == "application/json"
        
        parsed = json.loads(result.data.decode())
        assert "data" in parsed


# ==================== BULK IMPORT TESTS ====================

class TestBulkImport:
    """Tests for bulk import."""
    
    @pytest.mark.asyncio
    async def test_csv_import(self):
        """Test CSV import."""
        from app.services.bulk_import import get_import_service
        
        service = get_import_service()
        
        csv_content = b"project_name,city,roof_area_sqm\nTest Project,Mumbai,100\nAnother Project,Delhi,150"
        
        result = await service.import_projects(csv_content, "csv")
        
        assert result.success_count == 2
        assert result.error_count == 0
    
    def test_template_generation(self):
        """Test CSV template generation."""
        from app.services.bulk_import import get_import_service
        
        service = get_import_service()
        
        filename, content = service.get_template("projects")
        
        assert filename.endswith(".csv")
        assert b"project_name" in content


# ==================== HEALTH DASHBOARD TESTS ====================

class TestHealthDashboard:
    """Tests for health dashboard."""
    
    @pytest.mark.asyncio
    async def test_health_summary(self):
        """Test health summary."""
        from app.services.health_dashboard import get_health_service
        
        service = get_health_service()
        
        summary = await service.get_health_summary()
        
        assert "status" in summary
        assert "uptime" in summary
        assert "checks" in summary
    
    @pytest.mark.asyncio
    async def test_database_check(self):
        """Test database health check."""
        from app.services.health_dashboard import get_health_service
        
        service = get_health_service()
        
        result = await service.check_database()
        
        assert result.name == "database"
        assert result.status in ["healthy", "degraded", "unhealthy"]


# ==================== ANALYTICS DASHBOARD TESTS ====================

class TestAnalyticsDashboard:
    """Tests for analytics dashboard."""
    
    @pytest.mark.asyncio
    async def test_dashboard_summary(self):
        """Test dashboard summary."""
        from app.services.analytics_dashboard import get_analytics_service, TimeRange
        
        service = get_analytics_service()
        
        summary = await service.get_dashboard_summary(time_range=TimeRange.MONTH)
        
        assert "cards" in summary
        assert "period" in summary
        assert len(summary["cards"]) > 0
    
    @pytest.mark.asyncio
    async def test_geographic_distribution(self):
        """Test geographic distribution."""
        from app.services.analytics_dashboard import get_analytics_service
        
        service = get_analytics_service()
        
        result = await service.get_geographic_distribution()
        
        assert "data" in result
        assert "total" in result


# ==================== WEBSOCKET TESTS ====================

class TestWebSocket:
    """Tests for WebSocket service."""
    
    def test_connection_manager_stats(self):
        """Test connection manager statistics."""
        from app.services.websocket_service import get_connection_manager
        
        manager = get_connection_manager()
        stats = manager.get_connection_stats()
        
        assert "total_connections" in stats
        assert "unique_users" in stats


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
