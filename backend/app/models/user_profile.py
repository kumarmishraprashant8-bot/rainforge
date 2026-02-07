"""
User Profile Models
Database models for user profiles, KYC, and preferences.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

# Import base from existing models
try:
    from app.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class KYCStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"


class UserProfile(Base):
    """Complete user profile with KYC and preferences."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True_)
    
    # Basic Info
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(15), nullable=False)
    alternate_phone = Column(String(15))
    
    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(6))
    
    # KYC
    aadhaar_number_hash = Column(String(64))  # Hashed for security
    aadhaar_last_four = Column(String(4))
    aadhaar_verified = Column(Boolean, default=False)
    pan_number = Column(String(10))
    voter_id = Column(String(20))
    kyc_status = Column(String(20), default="pending")
    kyc_verified_at = Column(DateTime)
    kyc_verified_by = Column(Integer)
    
    # Preferences
    preferred_language = Column(String(5), default="en")
    preferred_payment_mode = Column(String(20), default="upi")
    
    # Notifications
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    whatsapp_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    bank_details = relationship("BankDetail", back_populates="user_profile", uselist=False)
    properties = relationship("PropertyDetail", back_populates="user_profile")
    financial_details = relationship("FinancialDetail", back_populates="user_profile", uselist=False)


class BankDetail(Base):
    """Bank account details for subsidy disbursement."""
    __tablename__ = "bank_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"))
    
    # Account Info
    account_holder_name = Column(String(100), nullable=False)
    account_number_encrypted = Column(String(256), nullable=False)  # Encrypted
    account_number_last_four = Column(String(4))
    ifsc_code = Column(String(11), nullable=False)
    bank_name = Column(String(100))
    branch_name = Column(String(100))
    account_type = Column(String(20), default="savings")
    
    # UPI
    upi_id = Column(String(50))
    
    # Verification
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    penny_drop_status = Column(String(20))  # pending, success, failed
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="bank_details")


class PropertyDetail(Base):
    """Property details for RWH assessment."""
    __tablename__ = "property_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Property Type
    property_type = Column(String(50), default="residential_individual")
    ownership_status = Column(String(30), default="owner")
    
    # Registration
    property_registration_number = Column(String(50))
    property_tax_id = Column(String(50))
    electricity_consumer_number = Column(String(50))
    water_connection_number = Column(String(50))
    
    # Building Details
    building_name = Column(String(100))
    plot_number = Column(String(50))
    ward_number = Column(String(20))
    gram_panchayat = Column(String(100))
    
    # Existing RWH
    existing_rwh_system = Column(Boolean, default=False)
    existing_rwh_type = Column(String(50))
    existing_rwh_capacity = Column(Float)
    
    # Area
    plot_area_sqm = Column(Float)
    built_up_area_sqm = Column(Float)
    open_area_sqm = Column(Float, default=0)
    
    # Building Specifics
    num_floors = Column(Integer, default=1)
    building_age_years = Column(Integer, default=0)
    construction_year = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="properties")
    roof_zones = relationship("RoofZone", back_populates="property")


class RoofZone(Base):
    """Individual roof zones for multi-zone assessments."""
    __tablename__ = "roof_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property_details.id"))
    
    # Zone Info
    zone_id = Column(String(50), nullable=False)
    zone_name = Column(String(100))
    
    # Characteristics
    area_sqm = Column(Float, nullable=False)
    roof_type = Column(String(30), default="rcc")
    roof_condition = Column(String(20), default="good")
    slope_degrees = Column(Integer, default=5)
    shade_coverage_percent = Column(Integer, default=0)
    
    # Calculated
    runoff_coefficient = Column(Float)
    effective_area_sqm = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    property = relationship("PropertyDetail", back_populates="roof_zones")


class FinancialDetail(Base):
    """Financial details for subsidy calculation."""
    __tablename__ = "financial_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"))
    
    # Income
    income_category = Column(String(20), default="not_disclosed")
    annual_income_range = Column(String(30))
    
    # BPL Status
    is_bpl = Column(Boolean, default=False)
    bpl_card_number = Column(String(30))
    apl_card_number = Column(String(30))
    ration_card_number = Column(String(30))
    
    # Budget
    budget_min_inr = Column(Float)
    budget_max_inr = Column(Float)
    
    # Financing
    needs_financing = Column(Boolean, default=False)
    emi_preference = Column(Boolean, default=False)
    preferred_emi_tenure_months = Column(Integer)
    
    # Insurance
    wants_insurance = Column(Boolean, default=False)
    
    # Water Expenses
    monthly_water_bill_inr = Column(Float, default=500)
    monthly_tanker_expense_inr = Column(Float, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="financial_details")
    subsidy_history = relationship("SubsidyHistory", back_populates="financial_detail")


class SubsidyHistory(Base):
    """Previous subsidies availed by user."""
    __tablename__ = "subsidy_history"
    
    id = Column(Integer, primary_key=True, index=True)
    financial_detail_id = Column(Integer, ForeignKey("financial_details.id"))
    
    # Subsidy Info
    scheme_name = Column(String(100), nullable=False)
    amount_received = Column(Float, nullable=False)
    year_availed = Column(Integer, nullable=False)
    certificate_number = Column(String(50))
    
    # Verification
    verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    financial_detail = relationship("FinancialDetail", back_populates="subsidy_history")
