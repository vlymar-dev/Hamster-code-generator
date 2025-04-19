import logging
from typing import Any, Callable, Coroutine, TypeVar

from pydantic import BaseModel
from redis.asyncio import Redis

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)


class CacheService:
    """Service for caching operations using Redis with model validation."""

    def __init__(self, redis: Redis, default_ttl: int = 3600):
        """Initialize with Redis connection and default TTL.

        Args:
            redis: Async Redis client
            default_ttl: Default cache lifetime in seconds
        """
        self.redis = redis
        self.default_ttl = default_ttl
        logger.debug(f'CacheService initialized with TTL {default_ttl}')

    async def get(self, key: str, model: type[T]) -> T | None:
        """Get cached value and validate against model.

        Args:
            key: Cache key
            model: Pydantic model for validation

        Returns:
            Parsed model instance or None if not found
        """
        logger.debug(f'Fetching cache key: {key}')
        data = await self.redis.get(key)
        if data:
            logger.debug(f'Cache HIT: {key}')
            return model.model_validate_json(data)
        logger.debug(f'Cache MISS: {key}')
        return None

    async def set(self, key: str, value: BaseModel, ttl: int = None):
        """Cache data with automatic JSON serialization."""
        actual_ttl = ttl or self.default_ttl
        logger.debug(f'SET cache: {key} (ttl={actual_ttl}s)')
        await self.redis.setex(key, actual_ttl, value.model_dump_json())

    async def delete(self, *keys: str):
        """Purge cache entries."""
        logger.debug(f'DELETE cache keys: {keys}')
        await self.redis.delete(*keys)

    async def get_or_set(
        self,
        key: str,
        model: type[T],
        fetch_func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        ttl: int = None,
        **kwargs,
    ) -> T:
        """Smart cache access with fallback to fresh data."""
        if cached := await self.get(key, model):
            return cached

        logger.debug(f'Cache MISS, fetching fresh: {key}')
        fresh_data = await fetch_func(*args, **kwargs)
        await self.set(key, fresh_data, ttl)
        return fresh_data

    async def refresh(
        self, key: str, fetch_func: Callable[..., Coroutine[Any, Any, T]], *args, ttl: int | None = None, **kwargs
    ) -> T:
        """Force cache update with fresh data."""
        logger.info(f'FORCE REFRESH: {key}')
        await self.delete(key)
        fresh_data = await fetch_func(*args, **kwargs)
        await self.set(key, fresh_data, ttl)
        return fresh_data


class CacheKeys:
    """Namespace for cache key patterns."""

    USER_DATA = 'user:{user_id}'
    LANGUAGE = 'lang:{user_id}'
    STATS = 'stats:{user_id}'
