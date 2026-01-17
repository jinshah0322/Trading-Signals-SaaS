import redis.asyncio as aioredis
from typing import Optional
from app.config import settings


# Global Redis client
redis_client: Optional[aioredis.Redis] = None


async def create_redis_pool():
    """Create Redis connection pool"""
    global redis_client
    
    redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.REDIS_POOL_MAX_CONNECTIONS
    )
    
    # Test connection
    await redis_client.ping()
    print(f"Redis pool created (max_connections={settings.REDIS_POOL_MAX_CONNECTIONS})")
    
    return redis_client


async def close_redis_pool():
    """Close Redis connection pool"""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis pool closed")


def get_redis() -> aioredis.Redis:
    """Get the Redis client"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call create_redis_pool() first.")
    return redis_client