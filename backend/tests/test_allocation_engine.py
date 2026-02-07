"""
Comprehensive tests for Allocation Engine.
Tests all 3 allocation modes and scoring algorithms.
"""
import pytest
from app.services.allocation_engine import AllocationEngine, AllocationMode, Installer, Job, AllocationResult, AllocationWeights


class TestAllocationEngine:
    """Test suite for smart allocation engine."""
    
    @pytest.fixture
    def sample_installers(self):
        """Sample installer data for testing."""
        return [
            Installer(
                id=1,
                name="Alpha Corp",
                company="Alpha Corp",
                rpi_score=85,
                capacity_available=4,  # Score 40
                lat=28.6139,
                lng=77.2090,
                avg_cost_factor=1.0,
                sla_compliance_pct=0.95,
                is_blacklisted=False,
                jobs_completed=120
            ),
            Installer(
                id=2,
                name="Beta Services",
                company="Beta Services",
                rpi_score=92,
                capacity_available=5,  # Score 50
                lat=28.6200,
                lng=77.2150,
                avg_cost_factor=1.2, # High cost
                sla_compliance_pct=0.98,
                is_blacklisted=False,
                jobs_completed=80
            ),
            Installer(
                id=3,
                name="Gamma Install",
                company="Gamma Install",
                rpi_score=70,
                capacity_available=6,  # Score 60
                lat=28.6000,
                lng=77.2000,
                avg_cost_factor=0.8, # Low cost
                sla_compliance_pct=0.85,
                is_blacklisted=False,
                jobs_completed=200
            ),
            Installer(
                id=4,
                name="Delta Works",
                company="Delta Works",
                rpi_score=60,
                capacity_available=10, # Score 100
                lat=28.5900,
                lng=77.1900,
                avg_cost_factor=0.8,
                sla_compliance_pct=0.80,
                is_blacklisted=True,  # Blacklisted
                jobs_completed=50
            )
        ]
    
    @pytest.fixture
    def sample_job(self):
        """Sample job for allocation."""
        return Job(
            id=101,
            address="Test Address",
            lat=28.6100,
            lng=77.2050,
            estimated_cost_inr=50000,
            complexity="standard"
        )
    
    # ==================== MODE TESTS ====================
    
    def test_gov_optimized_prefers_high_rpi(self, sample_installers, sample_job):
        """Gov Optimized mode should prefer high-RPI installers."""
        # Gov optimized prioritizes RPI and SLA
        result = AllocationEngine.allocate(sample_job, sample_installers, mode=AllocationMode.GOV_OPTIMIZED)
        
        assert result is not None
        assert result.installer_id is not None
        # Should select installer with highest RPI (id=2, RPI=92)
        assert result.installer_id == 2
    
    def test_equitable_distributes_load(self, sample_installers, sample_job):
        """Equitable mode should balance work across installers."""
        # Manually adjust capacities to test logic
        # Installer 1 has 50 capacity, Installer 3 has 80.
        # Equitable mode weights capacity heavily (0.40).
        
        result = AllocationEngine.allocate(sample_job, sample_installers, mode=AllocationMode.EQUITABLE)
        
        assert result is not None
        # Should prefer installer with more capacity available (Installer 3 has 80 available)
        # Note: Installer 4 has 100 but is blacklisted.
        assert result.installer_id == 3
    
    def test_user_choice_returns_ranked_list(self, sample_installers, sample_job):
        """User Choice mode should return all installers ranked."""
        result = AllocationEngine.allocate(sample_job, sample_installers, mode=AllocationMode.USER_CHOICE)
        
        assert result is not None
        assert result.alternatives is not None
        # Should have 3 installers (excluding blacklisted #4 from total 4)
        # Result includes top 1 + alternatives. 
        # Actually allocate returns the top choice and alternatives list.
        # Total valid = 3. Top is 1, alternatives should be 2.
        
        # Check if result (top) + alternatives cover all valid installers
        all_ids = [result.installer_id] + [a["installer_id"] for a in result.alternatives]
        assert len(all_ids) == 3
        assert 4 not in all_ids
        
        # Verify sorting in alternatives
        alt_scores = [a["score"] for a in result.alternatives]
        assert alt_scores == sorted(alt_scores, reverse=True)
    
    # ==================== BLACKLIST TESTS ====================
    
    def test_blacklisted_installer_excluded(self, sample_installers, sample_job):
        """Blacklisted installers should never be allocated."""
        result = AllocationEngine.allocate(sample_job, sample_installers)
        
        # Installer 4 is blacklisted
        all_ids = [result.installer_id] + [a["installer_id"] for a in result.alternatives]
        assert 4 not in all_ids
    
    # ==================== SCORING TESTS ====================
    
    def test_distance_scoring(self, sample_installers, sample_job):
        """Closer installers should get higher distance scores."""
        weights = AllocationEngine.get_weights()
        
        # Calculate scores manually to verify distance component
        # Installer 1 is at 28.6139, 77.2090. Job is at 28.6100, 77.2050
        # This is very close.
        
        # Installer 2 is at 28.6200, 77.2150. Further away.
        
        score1 = AllocationEngine.score_installer(sample_installers[0], sample_job, weights)
        score2 = AllocationEngine.score_installer(sample_installers[1], sample_job, weights)
        
        dist1 = score1["breakdown"]["distance"]
        dist2 = score2["breakdown"]["distance"]
        
        # Closer one (dist1) should have higher distance score (assuming similar weights for both, which is true as they use same weights object)
        
        raw_dist1 = score1["raw_scores"]["distance"]
        raw_dist2 = score2["raw_scores"]["distance"]
        
        assert raw_dist1 > raw_dist2
    
    def test_weight_normalization(self):
        """Custom weights should be normalized to sum to 1."""
        weights = AllocationWeights(
            rpi=40,
            capacity=20,
            distance=20,
            cost_band=20,
            sla_history=0 # Add missing field
        )
        
        normalized = weights.normalize()
        total = normalized.capacity + normalized.rpi + normalized.cost_band + normalized.distance + normalized.sla_history
        assert abs(total - 1.0) < 0.01  # Should sum to ~1.0
    
    def test_rpi_score_impact(self, sample_installers, sample_job):
        """Higher RPI should result in higher allocation score."""
        # Set distinct custom weights to isolate RPI
        custom_weights = AllocationWeights(rpi=100, capacity=0, distance=0, cost_band=0, sla_history=0)
        
        result = AllocationEngine.allocate(sample_job, sample_installers, custom_weights=custom_weights)
        
        # With 100% RPI weight, should select highest RPI (installer 2 with 92)
        assert result.installer_id == 2
    
    # ==================== EDGE CASES ====================
    
    def test_empty_installers_list(self, sample_job):
        """Should raise ValueError for empty installer list."""
        with pytest.raises(ValueError):
            AllocationEngine.allocate(sample_job, [])
    
    def test_all_installers_blacklisted(self, sample_job):
        """Should raise ValueError if all installers are blacklisted."""
        all_blacklisted = [
            Installer(id=1, name="B1", company="B1", lat=28.6, lng=77.2, is_blacklisted=True),
            Installer(id=2, name="B2", company="B2", lat=28.6, lng=77.2, is_blacklisted=True)
        ]
        
        with pytest.raises(ValueError):
            AllocationEngine.allocate(sample_job, all_blacklisted)
    
    def test_single_installer(self, sample_job):
        """Should work with single available installer."""
        single = [
            Installer(id=1, name="Only One", company="Only", rpi_score=75,
                     capacity_available=10, lat=28.6, lng=77.2,
                     is_blacklisted=False)
        ]
        
        result = AllocationEngine.allocate(sample_job, single)
        
        assert result.installer_id == 1
    
    # ==================== CAPACITY TESTS ====================
    
    def test_zero_capacity_installer_ranked_lower(self, sample_job):
        """Installers with no capacity should be ranked lower."""
        # 1 has high RPI but 0 capacity
        i1 = Installer(id=1, name="I1", company="I1", rpi_score=95, capacity_available=0, capacity_max=10, lat=28.6, lng=77.2)
        # 2 has lower RPI but capacity available
        i2 = Installer(id=2, name="I2", company="I2", rpi_score=80, capacity_available=5, capacity_max=10, lat=28.6, lng=77.2)
        
        # Use Equitable mode to prioritize capacity, or custom weights
        custom_weights = AllocationWeights(capacity=80, rpi=20, distance=0, cost_band=0, sla_history=0)
        
        result = AllocationEngine.allocate(sample_job, [i1, i2], custom_weights=custom_weights)
        
        # Installer with capacity should be preferred
        assert result.installer_id == 2


class TestAllocationWeights:
    """Test weight configuration."""
    
    def test_default_weights(self):
        """Should have sensible default weights."""
        weights = AllocationEngine.get_weights()
        
        assert weights.rpi > 0
        assert weights.capacity > 0
    
    def test_custom_weights_applied(self):
        """Custom weights should be applied correctly."""
        # Use a fresh AllocationEngine config if possible or just test logic
        # Since set_admin_weights is a class method modifying class state, be careful.
        # Better to test the Logic of setting/getting.
        
        original = AllocationEngine.get_weights()
        
        try:
            custom = AllocationWeights(rpi=0.5, capacity=0.3, distance=0.1, cost_band=0.1, sla_history=0.0)
            AllocationEngine.set_admin_weights(custom)
            
            retrieved = AllocationEngine.get_weights()
            assert retrieved.rpi > retrieved.distance
            
        finally:
            # Restore defaults to not affect other tests
            AllocationEngine.set_admin_weights(original)


class TestHaversineDistance:
    """Test geographic distance calculations."""
    
    def test_same_location_zero_distance(self):
        """Same coordinates should have zero distance."""
        distance = AllocationEngine.haversine_distance(28.6, 77.2, 28.6, 77.2)
        
        assert distance == 0
    
    def test_known_distance(self):
        """Test against known distance."""
        # Delhi to Noida ~= 25km
        distance = AllocationEngine.haversine_distance(28.6139, 77.2090, 28.5355, 77.3910)
        
        # Should be approximately 20-30km
        assert 15 < distance < 35  # km
    
    def test_symmetric_distance(self):
        """Distance should be same in both directions."""
        d1 = AllocationEngine.haversine_distance(28.6, 77.2, 28.7, 77.3)
        d2 = AllocationEngine.haversine_distance(28.7, 77.3, 28.6, 77.2)
        
        assert abs(d1 - d2) < 0.001  # Within 1 meter (km scale)
