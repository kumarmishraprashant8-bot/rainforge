"""
Tests for RPI Calculator Service.
Tests scoring components and grade calculations.
"""
import pytest
from app.services.rpi_calculator import RPICalculator


class TestRPICalculator:
    """Test suite for RainForge Performance Index calculator."""
    
    @pytest.fixture
    def sample_installer_data(self):
        """Sample installer performance data."""
        return {
            "installer_id": 1,
            "design_match_score": 92,  # How well actual matches design
            "yield_accuracy_score": 88,  # Predicted vs actual yield
            "timeliness_score": 95,  # On-time completion rate
            "complaint_rate": 0.02,  # 2% complaint rate
            "maintenance_score": 85,  # Maintenance quality
            "jobs_completed": 50,
            "total_yield_liters": 500000,
            "expected_yield_liters": 520000
        }
    
    # ==================== COMPONENT SCORING ====================
    
    def test_design_match_component(self, sample_installer_data):
        """Design match should be weighted correctly."""
        calculator = RPICalculator()
        
        score = calculator.calculate_component_score(
            "design_match",
            sample_installer_data["design_match_score"]
        )
        
        assert 0 <= score <= 100
        assert score > 80  # Should be high for 92 input
    
    def test_yield_accuracy_component(self, sample_installer_data):
        """Yield accuracy should compare actual vs expected."""
        calculator = RPICalculator()
        
        score = calculator.calculate_yield_accuracy(
            actual=sample_installer_data["total_yield_liters"],
            expected=sample_installer_data["expected_yield_liters"]
        )
        
        # 500000 / 520000 = ~96% accuracy
        assert 90 <= score <= 100
    
    def test_complaint_rate_scoring(self):
        """Lower complaint rate should give higher score."""
        calculator = RPICalculator()
        
        # 0% complaints = perfect score
        score_zero = calculator.calculate_complaint_score(0.00)
        
        # 5% complaints = lower score
        score_high = calculator.calculate_complaint_score(0.05)
        
        assert score_zero > score_high
        assert score_zero >= 95
    
    def test_timeliness_component(self):
        """On-time completion should be scored."""
        calculator = RPICalculator()
        
        score = calculator.calculate_timeliness_score(
            on_time_jobs=45,
            total_jobs=50
        )
        
        # 90% on-time
        assert 85 <= score <= 95
    
    # ==================== AGGREGATE RPI ====================
    
    def test_aggregate_rpi_calculation(self, sample_installer_data):
        """RPI should be weighted average of components."""
        calculator = RPICalculator()
        
        rpi = calculator.calculate_rpi(sample_installer_data)
        
        assert isinstance(rpi, dict)
        assert "score" in rpi
        assert "grade" in rpi
        assert "components" in rpi
        assert 0 <= rpi["score"] <= 100
    
    def test_rpi_component_breakdown(self, sample_installer_data):
        """RPI should include component breakdown."""
        calculator = RPICalculator()
        
        rpi = calculator.calculate_rpi(sample_installer_data)
        
        components = rpi["components"]
        assert "design_match" in components
        assert "yield_accuracy" in components
        assert "timeliness" in components
        assert "complaints" in components
        assert "maintenance" in components
    
    # ==================== GRADE ASSIGNMENT ====================
    
    def test_grade_a_plus(self):
        """Score 95+ should be A+."""
        calculator = RPICalculator()
        
        grade = calculator.score_to_grade(97)
        
        assert grade == "A+"
    
    def test_grade_a(self):
        """Score 90-94 should be A."""
        calculator = RPICalculator()
        
        assert calculator.score_to_grade(92) == "A"
        assert calculator.score_to_grade(90) == "A"
    
    def test_grade_b(self):
        """Score 80-89 should be B."""
        calculator = RPICalculator()
        
        assert calculator.score_to_grade(85) == "B"
        assert calculator.score_to_grade(80) == "B"
    
    def test_grade_c(self):
        """Score 70-79 should be C."""
        calculator = RPICalculator()
        
        assert calculator.score_to_grade(75) == "C"
    
    def test_grade_d(self):
        """Score 60-69 should be D."""
        calculator = RPICalculator()
        
        assert calculator.score_to_grade(65) == "D"
    
    def test_grade_f(self):
        """Score below 60 should be F."""
        calculator = RPICalculator()
        
        assert calculator.score_to_grade(55) == "F"
        assert calculator.score_to_grade(30) == "F"
    
    # ==================== GRADE COLORS ====================
    
    def test_grade_color_mapping(self):
        """Grades should have appropriate colors."""
        calculator = RPICalculator()
        
        assert calculator.get_grade_color("A+") == "#22c55e"  # Green
        assert calculator.get_grade_color("A") == "#22c55e"
        assert calculator.get_grade_color("F") == "#ef4444"  # Red
    
    # ==================== IMPROVEMENT SUGGESTIONS ====================
    
    def test_improvement_suggestions_low_timeliness(self):
        """Should suggest improving timeliness when low."""
        calculator = RPICalculator()
        
        data = {
            "design_match_score": 90,
            "yield_accuracy_score": 90,
            "timeliness_score": 60,  # Low
            "complaint_rate": 0.01,
            "maintenance_score": 85,
            "jobs_completed": 10
        }
        
        rpi = calculator.calculate_rpi(data)
        suggestions = rpi.get("improvement_suggestions", [])
        
        # Should suggest improving timeliness
        timeliness_suggestion = any("timelin" in s.lower() for s in suggestions)
        assert timeliness_suggestion
    
    def test_improvement_suggestions_high_complaints(self):
        """Should suggest reducing complaints when high."""
        calculator = RPICalculator()
        
        data = {
            "design_match_score": 90,
            "yield_accuracy_score": 90,
            "timeliness_score": 95,
            "complaint_rate": 0.15,  # High - 15%
            "maintenance_score": 85,
            "jobs_completed": 10
        }
        
        rpi = calculator.calculate_rpi(data)
        suggestions = rpi.get("improvement_suggestions", [])
        
        # Should suggest addressing complaints
        complaint_suggestion = any("complaint" in s.lower() for s in suggestions)
        assert complaint_suggestion
    
    # ==================== EDGE CASES ====================
    
    def test_new_installer_default_score(self):
        """New installer with no jobs should get default score."""
        calculator = RPICalculator()
        
        new_installer = {
            "installer_id": 999,
            "jobs_completed": 0
        }
        
        rpi = calculator.calculate_rpi(new_installer)
        
        # Should get starting score (e.g., 70)
        assert 60 <= rpi["score"] <= 80
        assert rpi["grade"] in ["B", "C"]
    
    def test_perfect_score(self):
        """Perfect metrics should give 100."""
        calculator = RPICalculator()
        
        perfect = {
            "design_match_score": 100,
            "yield_accuracy_score": 100,
            "timeliness_score": 100,
            "complaint_rate": 0.0,
            "maintenance_score": 100,
            "jobs_completed": 100
        }
        
        rpi = calculator.calculate_rpi(perfect)
        
        assert rpi["score"] >= 98
        assert rpi["grade"] == "A+"


class TestRPIHistory:
    """Test RPI history tracking."""
    
    def test_history_recorded(self):
        """RPI changes should be recorded."""
        calculator = RPICalculator()
        
        history = calculator.get_rpi_history(installer_id=1, months=6)
        
        assert isinstance(history, list)
        # History items should have timestamp and score
        for entry in history:
            if entry:  # May be empty for new installers
                assert "timestamp" in entry or "month" in entry
                assert "score" in entry
    
    def test_trend_calculation(self):
        """Should calculate RPI trend."""
        calculator = RPICalculator()
        
        trend = calculator.calculate_trend(installer_id=1)
        
        assert trend in ["improving", "declining", "stable", "insufficient_data"]
