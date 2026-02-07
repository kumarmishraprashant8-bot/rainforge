"""
In-Memory Rate Limiter
Rate limiting without external dependencies
"""
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from functools import wraps

from fastapi import HTTPException, Request


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int  # Number of requests allowed
    window: int  # Time window in seconds
    
    @classmethod
    def per_second(cls, n: int) -> 'RateLimitConfig':
        return cls(requests=n, window=1)
    
    @classmethod
    def per_minute(cls, n: int) -> 'RateLimitConfig':
        return cls(requests=n, window=60)
    
    @classmethod
    def per_hour(cls, n: int) -> 'RateLimitConfig':
        return cls(requests=n, window=3600)


class RateLimiter:
    """
    In-memory sliding window rate limiter.
    
    No external dependencies required.
    Uses sliding window log algorithm for accurate limiting.
    """
    
    # Default limits by endpoint pattern
    DEFAULT_LIMITS = {
        "/api/v1/assessments": RateLimitConfig.per_minute(30),
        "/api/v1/auth/login": RateLimitConfig.per_minute(5),
        "/api/v1/auth/register": RateLimitConfig.per_hour(10),
        "/api/v1/verify/photo": RateLimitConfig.per_minute(10),
        "/api/v1/payments": RateLimitConfig.per_minute(20),
        "/api/v1/advanced": RateLimitConfig.per_minute(60),
        "default": RateLimitConfig.per_minute(100)
    }
    
    def __init__(self):
        # Store: {key: [timestamps]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        self._cleanup_interval = 60  # Cleanup every minute
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key."""
        return f"{identifier}:{endpoint}"
    
    def _get_limit(self, endpoint: str) -> RateLimitConfig:
        """Get rate limit for endpoint."""
        for pattern, limit in self.DEFAULT_LIMITS.items():
            if pattern in endpoint:
                return limit
        return self.DEFAULT_LIMITS["default"]
    
    def _cleanup_old_entries(self, key: str, window: int):
        """Remove entries outside the time window."""
        now = time.time()
        cutoff = now - window
        self._requests[key] = [ts for ts in self._requests[key] if ts > cutoff]
    
    def _global_cleanup(self):
        """Periodic cleanup of all old entries."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = now
        
        # Clean up empty keys
        empty_keys = [k for k, v in self._requests.items() if not v]
        for key in empty_keys:
            del self._requests[key]
    
    def check(
        self,
        identifier: str,
        endpoint: str,
        limit: RateLimitConfig = None
    ) -> Tuple[bool, Dict]:
        """
        Check if request is allowed.
        
        Returns:
            (allowed, info) - allowed is bool, info contains limit details
        """
        limit = limit or self._get_limit(endpoint)
        key = self._get_key(identifier, endpoint)
        now = time.time()
        
        # Cleanup
        self._cleanup_old_entries(key, limit.window)
        self._global_cleanup()
        
        # Check count
        current_count = len(self._requests[key])
        
        # Calculate reset time
        if self._requests[key]:
            oldest = min(self._requests[key])
            reset_at = oldest + limit.window
        else:
            reset_at = now + limit.window
        
        info = {
            "limit": limit.requests,
            "remaining": max(0, limit.requests - current_count),
            "reset": int(reset_at),
            "window": limit.window
        }
        
        if current_count >= limit.requests:
            return False, info
        
        # Record request
        self._requests[key].append(now)
        info["remaining"] = max(0, limit.requests - current_count - 1)
        
        return True, info
    
    def get_headers(self, info: Dict) -> Dict[str, str]:
        """Get rate limit headers for response."""
        return {
            "X-RateLimit-Limit": str(info["limit"]),
            "X-RateLimit-Remaining": str(info["remaining"]),
            "X-RateLimit-Reset": str(info["reset"])
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# FastAPI Middleware
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    limiter = get_rate_limiter()
    
    # Get identifier (IP or user ID)
    identifier = request.client.host if request.client else "unknown"
    
    # Check auth header for user ID
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Would decode JWT to get user ID in production
        identifier = f"user:{auth_header[-10:]}"
    
    endpoint = request.url.path
    
    # Skip rate limiting for some endpoints
    skip_paths = ["/health", "/docs", "/openapi.json", "/static"]
    if any(endpoint.startswith(p) for p in skip_paths):
        return await call_next(request)
    
    allowed, info = limiter.check(identifier, endpoint)
    
    if not allowed:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Try again in {info['reset'] - int(time.time())} seconds.",
                "retry_after": info["reset"]
            },
            headers=limiter.get_headers(info)
        )
    
    response = await call_next(request)
    
    # Add rate limit headers to response
    for header, value in limiter.get_headers(info).items():
        response.headers[header] = value
    
    return response


# Decorator for route-specific limits
def rate_limit(requests: int, window: int):
    """Decorator for custom rate limits on specific routes."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request:
                limiter = get_rate_limiter()
                identifier = request.client.host if request.client else "unknown"
                limit = RateLimitConfig(requests=requests, window=window)
                
                allowed, info = limiter.check(identifier, request.url.path, limit)
                
                if not allowed:
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Rate limit exceeded",
                            "retry_after": info["reset"] - int(time.time())
                        }
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
