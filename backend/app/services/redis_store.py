"""
Redis Session & Cache Store
Production-grade caching and session management
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

# Try importing redis
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory fallback")


@dataclass
class RateLimitInfo:
    """Rate limit tracking info."""
    user_id: str
    endpoint: str
    requests: int
    window_start: datetime
    limit: int
    remaining: int


class RedisStore:
    """
    Redis-based session, cache, and rate limiting store.
    
    Features:
    - User sessions
    - API response caching
    - Rate limiting per user/endpoint
    - Distributed locks
    - Pub/Sub for real-time events
    """
    
    # Key prefixes
    PREFIX_SESSION = "session:"
    PREFIX_CACHE = "cache:"
    PREFIX_RATE = "rate:"
    PREFIX_LOCK = "lock:"
    PREFIX_QUEUE = "queue:"
    PREFIX_USER = "user:"
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 3600
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[redis.Redis] = None
        self._fallback: Dict[str, Any] = {}  # In-memory fallback
    
    async def connect(self) -> bool:
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            logger.warning("Using in-memory fallback")
            return False
        
        try:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self._client.ping()
            logger.info("Connected to Redis")
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self._client = None
            return False
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
    
    # ==================== SESSION MANAGEMENT ====================
    
    async def create_session(
        self,
        user_id: str,
        data: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ) -> str:
        """Create a new session."""
        session_id = hashlib.sha256(
            f"{user_id}:{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:32]
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "data": data
        }
        
        key = f"{self.PREFIX_SESSION}{session_id}"
        
        if self._client:
            await self._client.setex(key, ttl, json.dumps(session_data))
        else:
            self._fallback[key] = session_data
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        key = f"{self.PREFIX_SESSION}{session_id}"
        
        if self._client:
            data = await self._client.get(key)
            return json.loads(data) if data else None
        else:
            return self._fallback.get(key)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        key = f"{self.PREFIX_SESSION}{session_id}"
        
        if self._client:
            return await self._client.delete(key) > 0
        else:
            return self._fallback.pop(key, None) is not None
    
    async def extend_session(self, session_id: str, ttl: int = 86400) -> bool:
        """Extend session TTL."""
        key = f"{self.PREFIX_SESSION}{session_id}"
        
        if self._client:
            return await self._client.expire(key, ttl)
        return True
    
    # ==================== CACHING ====================
    
    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set cache value."""
        cache_key = f"{self.PREFIX_CACHE}{key}"
        ttl = ttl or self.default_ttl
        
        if self._client:
            await self._client.setex(cache_key, ttl, json.dumps(value))
        else:
            self._fallback[cache_key] = value
        return True
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        cache_key = f"{self.PREFIX_CACHE}{key}"
        
        if self._client:
            data = await self._client.get(cache_key)
            return json.loads(data) if data else None
        else:
            return self._fallback.get(cache_key)
    
    async def cache_delete(self, key: str) -> bool:
        """Delete cached value."""
        cache_key = f"{self.PREFIX_CACHE}{key}"
        
        if self._client:
            return await self._client.delete(cache_key) > 0
        return self._fallback.pop(cache_key, None) is not None
    
    async def cache_get_or_set(
        self,
        key: str,
        factory,
        ttl: Optional[int] = None
    ) -> Any:
        """Get from cache or compute and cache."""
        value = await self.cache_get(key)
        if value is not None:
            return value
        
        # Compute value
        if callable(factory):
            value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
        else:
            value = factory
        
        await self.cache_set(key, value, ttl)
        return value
    
    # ==================== RATE LIMITING ====================
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int = 100,
        window_seconds: int = 60
    ) -> RateLimitInfo:
        """
        Check and update rate limit.
        Returns rate limit info including whether request is allowed.
        """
        key = f"{self.PREFIX_RATE}{identifier}:{endpoint}"
        now = datetime.utcnow()
        
        if self._client:
            # Use Redis pipeline for atomic operations
            async with self._client.pipeline(transaction=True) as pipe:
                # Get current count
                await pipe.get(key)
                await pipe.ttl(key)
                results = await pipe.execute()
                
                current = int(results[0]) if results[0] else 0
                ttl = results[1] if results[1] > 0 else window_seconds
                
                if current >= limit:
                    return RateLimitInfo(
                        user_id=identifier,
                        endpoint=endpoint,
                        requests=current,
                        window_start=now - timedelta(seconds=window_seconds - ttl),
                        limit=limit,
                        remaining=0
                    )
                
                # Increment
                await pipe.incr(key)
                if current == 0:
                    await pipe.expire(key, window_seconds)
                await pipe.execute()
                
                return RateLimitInfo(
                    user_id=identifier,
                    endpoint=endpoint,
                    requests=current + 1,
                    window_start=now,
                    limit=limit,
                    remaining=limit - current - 1
                )
        else:
            # In-memory fallback
            if key not in self._fallback:
                self._fallback[key] = {"count": 0, "start": now}
            
            info = self._fallback[key]
            if (now - info["start"]).seconds > window_seconds:
                info = {"count": 0, "start": now}
                self._fallback[key] = info
            
            info["count"] += 1
            
            return RateLimitInfo(
                user_id=identifier,
                endpoint=endpoint,
                requests=info["count"],
                window_start=info["start"],
                limit=limit,
                remaining=max(0, limit - info["count"])
            )
    
    # ==================== USER QUOTAS ====================
    
    async def get_user_quota(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get user's API quota status."""
        key = f"{self.PREFIX_USER}{user_id}:quota"
        
        if self._client:
            data = await self._client.hgetall(key)
            return {k: int(v) for k, v in data.items()} if data else {}
        return {}
    
    async def increment_user_usage(
        self,
        user_id: str,
        metric: str,
        amount: int = 1
    ) -> int:
        """Increment user usage metric."""
        key = f"{self.PREFIX_USER}{user_id}:quota"
        
        if self._client:
            return await self._client.hincrby(key, metric, amount)
        return 0
    
    # ==================== DISTRIBUTED LOCKS ====================
    
    async def acquire_lock(
        self,
        lock_name: str,
        ttl: int = 30
    ) -> Optional[str]:
        """Acquire a distributed lock."""
        key = f"{self.PREFIX_LOCK}{lock_name}"
        lock_value = hashlib.sha256(
            f"{lock_name}:{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:16]
        
        if self._client:
            acquired = await self._client.set(key, lock_value, nx=True, ex=ttl)
            return lock_value if acquired else None
        else:
            if key not in self._fallback:
                self._fallback[key] = lock_value
                return lock_value
            return None
    
    async def release_lock(
        self,
        lock_name: str,
        lock_value: str
    ) -> bool:
        """Release a distributed lock."""
        key = f"{self.PREFIX_LOCK}{lock_name}"
        
        if self._client:
            # Only release if we own the lock
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            return await self._client.eval(script, 1, key, lock_value) == 1
        else:
            if self._fallback.get(key) == lock_value:
                del self._fallback[key]
                return True
            return False
    
    # ==================== QUEUE OPERATIONS ====================
    
    async def queue_push(
        self,
        queue_name: str,
        item: Dict[str, Any]
    ) -> int:
        """Push item to queue."""
        key = f"{self.PREFIX_QUEUE}{queue_name}"
        
        if self._client:
            return await self._client.rpush(key, json.dumps(item))
        else:
            if key not in self._fallback:
                self._fallback[key] = []
            self._fallback[key].append(item)
            return len(self._fallback[key])
    
    async def queue_pop(
        self,
        queue_name: str,
        timeout: int = 0
    ) -> Optional[Dict]:
        """Pop item from queue."""
        key = f"{self.PREFIX_QUEUE}{queue_name}"
        
        if self._client:
            if timeout > 0:
                result = await self._client.blpop(key, timeout)
                return json.loads(result[1]) if result else None
            else:
                data = await self._client.lpop(key)
                return json.loads(data) if data else None
        else:
            if key in self._fallback and self._fallback[key]:
                return self._fallback[key].pop(0)
            return None
    
    async def queue_length(self, queue_name: str) -> int:
        """Get queue length."""
        key = f"{self.PREFIX_QUEUE}{queue_name}"
        
        if self._client:
            return await self._client.llen(key)
        return len(self._fallback.get(key, []))


# Need asyncio for cache_get_or_set
import asyncio

# Singleton
_store: Optional[RedisStore] = None

async def get_redis_store() -> RedisStore:
    global _store
    if _store is None:
        from app.core.config import settings
        _store = RedisStore(redis_url=getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))
        await _store.connect()
    return _store
