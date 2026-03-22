"""Redis Connection Management"""

from typing import Optional
import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import logger


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self._session_client: Optional[Redis] = None
        self._cache_client: Optional[Redis] = None
    
    async def get_session_client(self) -> Redis:
        """Get Redis client for session storage"""
        if self._session_client is None:
            self._session_client = await redis.from_url(
                settings.redis_session_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis session client connected")
        return self._session_client
    
    async def get_cache_client(self) -> Redis:
        """Get Redis client for caching"""
        if self._cache_client is None:
            self._cache_client = await redis.from_url(
                settings.redis_cache_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis cache client connected")
        return self._cache_client
    
    async def close(self):
        """Close Redis connections"""
        if self._session_client:
            await self._session_client.close()
            logger.info("Redis session client closed")
        if self._cache_client:
            await self._cache_client.close()
            logger.info("Redis cache client closed")


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_session() -> Redis:
    """Dependency for getting Redis session client"""
    return await redis_client.get_session_client()


async def get_redis_cache() -> Redis:
    """Dependency for getting Redis cache client"""
    return await redis_client.get_cache_client()
