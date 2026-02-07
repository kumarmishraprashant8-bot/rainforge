"""Authentication API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    hash_password,
    TokenData
)

router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# In-memory user store (replace with database in production)
USERS_DB: dict = {}


# ============== SCHEMAS ==============

class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="user", pattern="^(user|installer|admin)$")
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """User response (no password)."""
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# ============== DEPENDENCIES ==============

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    if token_data.token_type != "access":
        raise credentials_exception
    
    return token_data


async def get_current_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_installer(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require installer or admin role."""
    if current_user.role not in ["installer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Installer access required"
        )
    return current_user


# ============== ENDPOINTS ==============

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user."""
    if user.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_id = f"user_{len(USERS_DB) + 1}"
    USERS_DB[user.email] = {
        "id": user_id,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "role": user.role,
        "phone": user.phone,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    return {
        "message": "User registered successfully",
        "user_id": user_id
    }


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT tokens."""
    user = USERS_DB.get(form.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return TokenResponse(
        access_token=create_access_token(form.username, user["role"]),
        refresh_token=create_refresh_token(form.username, user["role"])
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    token_data = decode_token(request.refresh_token)
    
    if token_data is None or token_data.token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = USERS_DB.get(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return TokenResponse(
        access_token=create_access_token(token_data.user_id, user["role"]),
        refresh_token=create_refresh_token(token_data.user_id, user["role"])
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user's profile."""
    user = USERS_DB.get(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        created_at=user["created_at"]
    )


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    current_user: TokenData = Depends(get_current_user)
):
    """Change current user's password."""
    user = USERS_DB.get(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    user["password_hash"] = hash_password(request.new_password)
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """Logout user (client should discard tokens)."""
    # In production, add token to blacklist in Redis
    return {"message": "Logged out successfully"}
