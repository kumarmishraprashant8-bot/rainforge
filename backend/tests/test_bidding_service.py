"""
Tests for Bidding Service.
Tests bid submission, ranking, and award functionality.
"""
import pytest
from datetime import datetime, timedelta
from app.services.bidding_service import BiddingService, Bid, BidStatus


class TestBiddingService:
    """Test suite for competitive bidding service."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset bidding service state."""
        BiddingService.clear_all_bids()
    
    @pytest.fixture
    def sample_bids(self):
        """Sample bids for testing."""
        return [
            Bid(
                id=1,
                job_id=101,
                installer_id=1,
                amount=45000,
                timeline_days=7,
                warranty_months=12,
                installer_rpi=85,
                submitted_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Bid(
                id=2,
                job_id=101,
                installer_id=2,
                amount=42000,  # Lowest price
                timeline_days=10,
                warranty_months=6,
                installer_rpi=78,
                submitted_at=datetime.utcnow() - timedelta(hours=1)
            ),
            Bid(
                id=3,
                job_id=101,
                installer_id=3,
                amount=50000,
                timeline_days=5,  # Fastest
                warranty_months=24,  # Best warranty
                installer_rpi=92,  # Highest RPI
                submitted_at=datetime.utcnow()
            )
        ]
    
    # ==================== BID SUBMISSION ====================
    
    def test_submit_valid_bid(self):
        """Valid bid should be accepted."""
        service = BiddingService()
        
        bid = service.submit_bid(
            job_id=101,
            installer_id=1,
            amount=45000,
            timeline_days=7,
            warranty_months=12
        )
        
        assert bid is not None
        assert bid.id > 0
        assert bid.status == BidStatus.PENDING
    
    def test_submit_bid_below_minimum_rejected(self):
        """Bid below minimum threshold should be rejected."""
        service = BiddingService()
        
        with pytest.raises(ValueError):
            service.submit_bid(
                job_id=101,
                installer_id=1,
                amount=100,  # Too low
                timeline_days=7,
                warranty_months=12
            )
    
    def test_duplicate_bid_replaces_previous(self):
        """Same installer bidding again should replace."""
        service = BiddingService()
        
        bid1 = service.submit_bid(job_id=101, installer_id=1, amount=45000, timeline_days=7, warranty_months=12)
        bid2 = service.submit_bid(job_id=101, installer_id=1, amount=42000, timeline_days=6, warranty_months=12)
        
        bids = service.get_bids_for_job(101)
        assert len(bids) == 1
        assert bids[0].amount == 42000
    
    # ==================== BID RANKING ====================
    
    def test_composite_score_calculation(self, sample_bids):
        """Composite score should consider all factors."""
        service = BiddingService()
        
        for bid in sample_bids:
            service._bids[bid.id] = bid
        
        ranked = service.rank_bids(job_id=101)
        
        assert len(ranked) == 3
        # All should have scores
        for bid in ranked:
            assert hasattr(bid, 'composite_score')
            assert 0 <= bid.composite_score <= 100
    
    def test_ranking_order(self, sample_bids):
        """Bids should be ranked by composite score."""
        service = BiddingService()
        
        for bid in sample_bids:
            service._bids[bid.id] = bid
        
        ranked = service.rank_bids(job_id=101)
        
        scores = [b.composite_score for b in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_price_weight_in_scoring(self):
        """Lower price should improve score."""
        service = BiddingService()
        
        # Two identical bids except price
        service.submit_bid(job_id=101, installer_id=1, amount=50000, timeline_days=7, warranty_months=12)
        service.submit_bid(job_id=101, installer_id=2, amount=40000, timeline_days=7, warranty_months=12)
        
        ranked = service.rank_bids(101)
        
        # Lower price should rank higher
        assert ranked[0].installer_id == 2
    
    # ==================== BID AWARD ====================
    
    def test_award_bid(self, sample_bids):
        """Should be able to award a bid."""
        service = BiddingService()
        
        for bid in sample_bids:
            service._bids[bid.id] = bid
        
        result = service.award_bid(bid_id=3, awarded_by="admin@rainforge.in")
        
        assert result is not None
        assert result.status == BidStatus.AWARDED
        assert result.awarded_at is not None
    
    def test_award_rejects_other_bids(self, sample_bids):
        """Awarding one bid should reject others."""
        service = BiddingService()
        
        for bid in sample_bids:
            service._bids[bid.id] = bid
        
        service.award_bid(bid_id=3)
        
        # Other bids should be rejected
        assert service._bids[1].status == BidStatus.REJECTED
        assert service._bids[2].status == BidStatus.REJECTED
    
    def test_cannot_award_already_awarded_job(self, sample_bids):
        """Cannot award bid if job already has winner."""
        service = BiddingService()
        
        for bid in sample_bids:
            service._bids[bid.id] = bid
        
        service.award_bid(bid_id=1)
        
        with pytest.raises(ValueError):
            service.award_bid(bid_id=2)
    
    # ==================== BID STATUS ====================
    
    def test_bid_status_transitions(self):
        """Bid status should transition correctly."""
        service = BiddingService()
        
        bid = service.submit_bid(job_id=101, installer_id=1, amount=45000, timeline_days=7, warranty_months=12)
        
        assert bid.status == BidStatus.PENDING
        
        service.award_bid(bid.id)
        
        updated = service.get_bid(bid.id)
        assert updated.status == BidStatus.AWARDED
    
    # ==================== BID WINDOW ====================
    
    def test_open_bidding_window(self):
        """Should be able to open bidding window."""
        service = BiddingService()
        
        window = service.open_bidding(job_id=101, duration_hours=72)
        
        assert window is not None
        assert window["job_id"] == 101
        assert window["closes_at"] > datetime.utcnow()
    
    def test_submit_after_window_closed_rejected(self):
        """Bids after window closes should be rejected."""
        service = BiddingService()
        
        # Open window that's already closed
        service.open_bidding(job_id=101, duration_hours=-1)  # Negative = already closed
        
        with pytest.raises(ValueError):
            service.submit_bid(job_id=101, installer_id=1, amount=45000, timeline_days=7, warranty_months=12)


class TestBidScoring:
    """Test bid scoring algorithms."""
    
    def test_price_score(self):
        """Lower prices should score higher."""
        service = BiddingService()
        
        min_price, max_price = 30000, 60000
        
        score_low = service._calculate_price_score(30000, min_price, max_price)
        score_high = service._calculate_price_score(60000, min_price, max_price)
        
        assert score_low > score_high
        assert score_low == 100  # Lowest price = max score
    
    def test_timeline_score(self):
        """Faster timelines should score higher."""
        service = BiddingService()
        
        score_fast = service._calculate_timeline_score(5)
        score_slow = service._calculate_timeline_score(14)
        
        assert score_fast > score_slow
    
    def test_warranty_score(self):
        """Longer warranties should score higher."""
        service = BiddingService()
        
        score_long = service._calculate_warranty_score(24)
        score_short = service._calculate_warranty_score(6)
        
        assert score_long > score_short
    
    def test_rpi_included_in_composite(self):
        """Installer RPI should be factored in."""
        service = BiddingService()
        
        bid_high_rpi = Bid(id=1, job_id=101, installer_id=1, amount=45000, 
                          timeline_days=7, warranty_months=12, installer_rpi=95)
        bid_low_rpi = Bid(id=2, job_id=101, installer_id=2, amount=45000,
                         timeline_days=7, warranty_months=12, installer_rpi=60)
        
        score_high = service._calculate_composite_score(bid_high_rpi)
        score_low = service._calculate_composite_score(bid_low_rpi)
        
        assert score_high > score_low
