from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # owner, installer, municipal

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String)
    # PostGIS Polygon for roof footprint
    roof_geometry = Column(Geometry('POLYGON', srid=4326))
    roof_area_sqm = Column(Float)
    roof_material = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    assessment = relationship("Assessment", back_populates="project", uselist=False)

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    annual_yield_liters = Column(Float)
    recommended_storage_liters = Column(Float)
    bom_data = Column(JSON)  # Store Bill of Materials as JSON
    cost_estimate = Column(Float)

class Contractor(Base):
    __tablename__ = "contractors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    # Contractor service area
    service_area = Column(Geometry('POLYGON', srid=4326))
    rating = Column(Float)
