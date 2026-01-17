from typing import Optional
from app.redis_client import get_redis

async def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    redis = get_redis()
    
    # Get current count
    current_count = await redis.get(key)
    
    if current_count is None:
        # First request - set counter to 1 with expiry
        await redis.setex(key, window_seconds, 1)
        return True
    
    current_count = int(current_count)
    
    # Check if limit exceeded
    if current_count >= max_requests:
        return False
    
    # Increment counter
    await redis.incr(key)
    return True


async def get_rate_limit_ttl(key: str) -> int:
    redis = get_redis()
    ttl = await redis.ttl(key)
    return ttl if ttl > 0 else 0


async def get_cached_data(key: str) -> Optional[str]:
    redis = get_redis()
    return await redis.get(key)


async def set_cached_data(key: str, value: str, expire_seconds: int) -> bool:
    redis = get_redis()
    await redis.setex(key, expire_seconds, value)
    return True


async def delete_cached_data(key: str) -> bool:
    redis = get_redis()
    result = await redis.delete(key)
    return result > 0