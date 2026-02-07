"""Security utilities for RainForge API."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # User ID or email
    exp: datetime
    type: str  # "access" or "refresh"
    role: str  # "user", "installer", "admin"
    iat: datetime


class TokenData(BaseModel):
    """Extracted token data for authentication."""
    user_id: str
    role: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(user_id: str, role: str = "user") -> str:
    """Create a short-lived access token."""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "type": "access",
        "role": role
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str, role: str = "user") -> str:
    """Create a long-lived refresh token."""
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "type": "refresh",
        "role": role
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return TokenData(
            user_id=payload["sub"],
            role=payload.get("role", "user"),
            token_type=payload.get("type", "access")
        )
    except JWTError:
        return None


def create_device_token(device_id: str, project_id: int) -> str:
    """Create a long-lived token for IoT device authentication."""
    now = datetime.utcnow()
    expire = now + timedelta(days=365)  # 1 year for devices
    payload = {
        "sub": device_id,
        "project_id": project_id,
        "exp": expire,
        "iat": now,
        "type": "device"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def validate_device_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate an IoT device token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "device":
            return None
        return {
            "device_id": payload["sub"],
            "project_id": payload.get("project_id")
        }
    except JWTError:
        return None
