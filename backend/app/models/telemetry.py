from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    flow_rate = Column(Float)
    total_volume = Column(Float)
    battery_voltage = Column(Float)
    ph_level = Column(Float)
    turbidity = Column(Float)
    
    # TimescaleDB hypertable creation would happen in migration script
    # SELECT create_hypertable('telemetry', 'timestamp');
