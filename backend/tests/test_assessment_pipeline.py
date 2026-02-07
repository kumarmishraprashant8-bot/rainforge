"""
Unit tests for Feature A: multi-modal assessment pipeline.
Tests pipeline selector and confidence per mode.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.assessment_pipeline import (
    AssessmentMode,
    select_pipeline,
    get_confidence_for_mode,
    run_pipeline,
)


class TestPipelineSelector:
    """Unit tests for pipeline selector."""

    def test_select_pipeline_none_returns_address(self):
        assert select_pipeline(None) == AssessmentMode.ADDRESS

    def test_select_pipeline_empty_returns_address(self):
        assert select_pipeline("") == AssessmentMode.ADDRESS

    def test_select_pipeline_address_returns_address(self):
        assert select_pipeline("address") == AssessmentMode.ADDRESS

    def test_select_pipeline_satellite_only(self):
        assert select_pipeline("satellite-only") == AssessmentMode.SATELLITE_ONLY

    def test_select_pipeline_satellite_alias(self):
        assert select_pipeline("satellite") == AssessmentMode.SATELLITE_ONLY

    def test_select_pipeline_photo(self):
        assert select_pipeline("photo") == AssessmentMode.PHOTO

    def test_select_pipeline_unknown_returns_address(self):
        assert select_pipeline("unknown") == AssessmentMode.ADDRESS


class TestConfidenceForMode:
    """Unit tests for confidence score by mode."""

    def test_confidence_address(self):
        assert get_confidence_for_mode(AssessmentMode.ADDRESS) == 85.0

    def test_confidence_satellite_only(self):
        assert get_confidence_for_mode(AssessmentMode.SATELLITE_ONLY) == 72.0

    def test_confidence_photo(self):
        assert get_confidence_for_mode(AssessmentMode.PHOTO) == 65.0


class TestRunPipeline:
    """Integration-style tests for run_pipeline (requires DB)."""

    @pytest.fixture
    def db_session(self):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        from app.models.database import init_db, SessionLocal
        init_db()
        session = SessionLocal()
        yield session
        session.close()

    def test_run_pipeline_requires_db(self):
        with pytest.raises(ValueError, match="db_session is required"):
            run_pipeline(
                mode=AssessmentMode.ADDRESS,
                address="123 Test St",
                db_session=None,
            )

    def test_run_pipeline_address_returns_pdf_url_and_confidence(self, db_session):
        result = run_pipeline(
            mode=AssessmentMode.ADDRESS,
            address="123 Gandhi Road, New Delhi",
            lat=28.6139,
            lng=77.2090,
            roof_area_sqm=120,
            roof_material="concrete",
            state="Delhi",
            city="New Delhi",
            db_session=db_session,
            pdf_base_path="assess",
        )
        assert "assessment_id" in result
        assert result["assessment_id"].startswith("ASM-")
        assert "pdf_url" in result
        assert "/pdf" in result["pdf_url"]
        assert "confidence" in result
        assert result["confidence"] == 85.0
        assert "scenarios" in result
        assert "max_capture" in result["scenarios"]

    def test_run_pipeline_satellite_only_uses_fallbacks_and_confidence(self, db_session):
        result = run_pipeline(
            mode=AssessmentMode.SATELLITE_ONLY,
            address="seeded address",
            db_session=db_session,
            pdf_base_path="assess",
        )
        assert result["mode"] == "satellite-only"
        assert result["confidence"] == 72.0
        assert "pdf_url" in result
        assert result["annual_yield_liters"] > 0

    def test_run_pipeline_photo_returns_confidence(self, db_session):
        result = run_pipeline(
            mode=AssessmentMode.PHOTO,
            address="",
            db_session=db_session,
            pdf_base_path="assess",
        )
        assert result["mode"] == "photo"
        assert result["confidence"] == 65.0
        assert "Photo-based" in result["address"] or result["address"]
        assert "pdf_url" in result
