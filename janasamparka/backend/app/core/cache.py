"""
Redis-based caching system for Janasamparka
"""
import json
import pickle
from typing import Any, Optional, Union, Callable, TypeVar, Dict
from functools import wraps
from datetime import timedelta
import hashlib

import redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import logger

# Generic type for cached functions
T = TypeVar('T')


class CacheManager:
    """Redis cache manager with async support"""
    
    def __init__(self):
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        self.redis_password = getattr(settings, 'REDIS_PASSWORD', None)
        self.default_ttl = getattr(settings, 'CACHE_TTL_DEFAULT', 300)
        self.long_ttl = getattr(settings, 'CACHE_TTL_LONG', 3600)
        
        # Initialize sync and async Redis clients
        self._redis_sync = None
        self._redis_async = None
    
    @property
    def redis_sync(self) -> redis.Redis:
        """Get synchronous Redis client"""
        if self._redis_sync is None:
            self._redis_sync = redis.Redis(
                from_url=self.redis_url,
                password=self.redis_password,
                decode_responses=True
            )
        return self._redis_sync
    
    @property
    def redis_async(self) -> AsyncRedis:
        """Get asynchronous Redis client"""
        if self._redis_async is None:
            self._redis_async = AsyncRedis.from_url(
                self.redis_url,
                password=self.redis_password,
                decode_responses=True
            )
        return self._redis_async
    
    def _make_key(self, prefix: str, key_parts: list) -> str:
        """Create a cache key from prefix and parts"""
        key_str = ":".join(str(part) for part in key_parts)
        full_key = f"{prefix}:{key_str}"
        
        # Hash long keys to avoid Redis key length limits
        if len(full_key) > 250:
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            return f"{prefix}:hashed:{key_hash}"
        
        return full_key
    
    async def get(self, prefix: str, key_parts: list) -> Optional[Any]:
        """Get value from cache"""
        try:
            key = self._make_key(prefix, key_parts)
            value = await self.redis_async.get(key)
            
            if value is None:
                return None
            
            # Try to deserialize as JSON first, then as pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                try:
                    return pickle.loads(value.encode('latin1'))
                except (pickle.PickleError, ValueError):
                    return value
                    
        except RedisError as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, prefix: str, key_parts: list, value: Any, 
                  ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            key = self._make_key(prefix, key_parts)
            ttl = ttl or self.default_ttl
            
            # Serialize value
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serialized = json.dumps(value, default=str)
            else:
                serialized = pickle.dumps(value).decode('latin1')
            
            result = await self.redis_async.setex(key, ttl, serialized)
            return result
            
        except RedisError as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, prefix: str, key_parts: list) -> bool:
        """Delete value from cache"""
        try:
            key = self._make_key(prefix, key_parts)
            result = await self.redis_async.delete(key)
            return result > 0
            
        except RedisError as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            keys = await self.redis_async.keys(pattern)
            if keys:
                return await self.redis_async.delete(*keys)
            return 0
            
        except RedisError as e:
            logger.error("Cache delete pattern failed", pattern=pattern, error=str(e))
            return 0
    
    async def exists(self, prefix: str, key_parts: list) -> bool:
        """Check if key exists in cache"""
        try:
            key = self._make_key(prefix, key_parts)
            result = await self.redis_async.exists(key)
            return result > 0
            
        except RedisError as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False
    
    async def increment(self, prefix: str, key_parts: list, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache"""
        try:
            key = self._make_key(prefix, key_parts)
            result = await self.redis_async.incrby(key, amount)
            return result
            
        except RedisError as e:
            logger.error("Cache increment failed", key=key, error=str(e))
            return None
    
    async def expire(self, prefix: str, key_parts: list, ttl: int) -> bool:
        """Set expiration on existing key"""
        try:
            key = self._make_key(prefix, key_parts)
            result = await self.redis_async.expire(key, ttl)
            return result
            
        except RedisError as e:
            logger.error("Cache expire failed", key=key, error=str(e))
            return False
    
    async def flush_all(self) -> bool:
        """Flush all cache data (use with caution)"""
        try:
            result = await self.redis_async.flushdb()
            return result
        except RedisError as e:
            logger.error("Cache flush failed", error=str(e))
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cached(prefix: str, ttl: Optional[int] = None, 
          key_builder: Optional[Callable] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Build cache key
            if key_builder:
                key_parts = key_builder(*args, **kwargs)
            else:
                # Default key building
                key_parts = []
                if args:
                    key_parts.extend(str(arg) for arg in args[1:])  # Skip 'self'
                if kwargs:
                    sorted_kwargs = sorted(kwargs.items())
                    key_parts.extend(f"{k}={v}" for k, v in sorted_kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(prefix, key_parts)
            if cached_result is not None:
                logger.debug("Cache hit", prefix=prefix, key=key_parts)
                return cached_result
            
            # Execute function and cache result
            logger.debug("Cache miss", prefix=prefix, key=key_parts)
            result = await func(*args, **kwargs)
            await cache_manager.set(prefix, key_parts, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_user_data(ttl: int = 1800):  # 30 minutes
    """Cache user-related data"""
    return cached("user", ttl=ttl)


def cache_constituency_data(ttl: int = 3600):  # 1 hour
    """Cache constituency-related data"""
    return cached("constituency", ttl=ttl)


def cache_department_data(ttl: int = 3600):  # 1 hour
    """Cache department-related data"""
    return cached("department", ttl=ttl)


def cache_complaint_stats(ttl: int = 300):  # 5 minutes
    """Cache complaint statistics"""
    return cached("complaint_stats", ttl=ttl)


def cache_analytics_data(ttl: int = 600):  # 10 minutes
    """Cache analytics data"""
    return cached("analytics", ttl=ttl)


class CacheInvalidation:
    """Cache invalidation utilities"""
    
    @staticmethod
    async def invalidate_user(user_id: str) -> bool:
        """Invalidate all cache entries for a user"""
        patterns = [
            f"user:*:{user_id}",
            f"complaint_stats:*:{user_id}",
            f"analytics:*:{user_id}"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache_manager.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info("User cache invalidated", user_id=user_id, deleted=total_deleted)
        return total_deleted > 0
    
    @staticmethod
    async def invalidate_constituency(constituency_id: str) -> bool:
        """Invalidate all cache entries for a constituency"""
        patterns = [
            f"constituency:*:{constituency_id}",
            f"department:*:{constituency_id}",
            f"ward:*:{constituency_id}",
            f"complaint_stats:*:{constituency_id}",
            f"analytics:*:{constituency_id}"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache_manager.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info("Constituency cache invalidated", 
                   constituency_id=constituency_id, deleted=total_deleted)
        return total_deleted > 0
    
    @staticmethod
    async def invalidate_complaint(complaint_id: str) -> bool:
        """Invalidate cache entries related to a complaint"""
        patterns = [
            f"complaint:*:{complaint_id}",
            f"complaint_stats:*",
            f"analytics:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache_manager.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info("Complaint cache invalidated", 
                   complaint_id=complaint_id, deleted=total_deleted)
        return total_deleted > 0
    
    @staticmethod
    async def invalidate_all_complaint_stats() -> bool:
        """Invalidate all complaint statistics"""
        deleted = await cache_manager.delete_pattern("complaint_stats:*")
        logger.info("All complaint stats cache invalidated", deleted=deleted)
        return deleted > 0


class CacheWarmer:
    """Cache warming utilities"""
    
    @staticmethod
    async def warm_constituency_data(db_session):
        """Warm cache with frequently accessed constituency data"""
        from app.models.constituency import Constituency
        from app.models.department import Department
        from app.models.ward import Ward
        
        try:
            # Cache all active constituencies
            constituencies = db_session.query(Constituency).filter(
                Constituency.is_active == True
            ).all()
            
            for constituency in constituencies:
                await cache_manager.set(
                    "constituency", ["id", str(constituency.id)], 
                    constituency.to_dict(), ttl=3600
                )
            
            # Cache departments for each constituency
            for constituency in constituencies:
                departments = db_session.query(Department).filter(
                    Department.constituency_id == constituency.id,
                    Department.is_active == True
                ).all()
                
                await cache_manager.set(
                    "department", ["by_constituency", str(constituency.id)],
                    [dept.to_dict() for dept in departments], ttl=3600
                )
            
            logger.info("Constituency cache warmed", 
                       constituencies=len(constituencies))
            
        except Exception as e:
            logger.error("Failed to warm constituency cache", error=str(e))
    
    @staticmethod
    async def warm_user_stats(db_session):
        """Warm cache with user statistics"""
        from app.models.user import User
        from sqlalchemy import func
        
        try:
            # Cache user counts by role
            role_counts = db_session.query(
                User.role, func.count(User.id)
            ).group_by(User.role).all()
            
            stats = {role: count for role, count in role_counts}
            await cache_manager.set(
                "analytics", ["user_counts"], stats, ttl=1800
            )
            
            logger.info("User stats cache warmed", stats=stats)
            
        except Exception as e:
            logger.error("Failed to warm user stats cache", error=str(e))


# Rate limiting cache utilities
class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed under rate limit"""
        current = await self.cache.increment("rate_limit", [key])
        
        if current == 1:
            # First request in window, set expiration
            await self.cache.expire("rate_limit", [key], window)
        
        return current <= limit
    
    async def get_remaining_requests(self, key: str, limit: int) -> int:
        """Get remaining requests in current window"""
        current = await self.cache.get("rate_limit", [key])
        if current is None:
            return limit
        return max(0, limit - current)


# Global rate limiter instance
rate_limiter = RateLimiter(cache_manager)
