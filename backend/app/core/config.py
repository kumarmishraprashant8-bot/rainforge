"""Core configuration for RainForge API."""
import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_TITLE: str = "RainForge API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Government-grade Rainwater Harvesting Platform"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION-" + os.urandom(16).hex())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - Production whitelist (accepts comma-separated string or JSON array)
    ALLOWED_ORIGINS: Union[List[str], str] = "http://localhost:5173,http://localhost:3000,https://rainforge.gov.in"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON first
            if v.startswith('['):
                try:
                    return json.loads(v)
                except:
                    pass
            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return ["http://localhost:5173"]
    
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@db:5432/rainforge"
    )
    TIMESCALE_URL: str = os.getenv(
        "TIMESCALE_URL",
        "postgresql://rainforge:telemetry123@timescale:5432/telemetry"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # MQTT
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "mqtt")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    
    # External APIs
    MAPBOX_TOKEN: str = os.getenv("MAPBOX_TOKEN", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    
    # Payment Gateway
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
