import pytest
import asyncio
from httpx import AsyncClient


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def clear_rate_limits():
    """Clear Redis rate limits before each test"""
    import redis.asyncio as aioredis
    try:
        redis_client = await aioredis.from_url("redis://redis:6379", decode_responses=True)
        keys = await redis_client.keys("rate_limit:*")
        if keys:
            await redis_client.delete(*keys)
        await redis_client.close()
    except Exception as e:
        print(f"Redis cleanup warning: {e}")
    
    yield


@pytest.fixture(scope="function")
async def client():
    """Create an async test client that connects to the running backend"""
    async with AsyncClient(base_url="http://localhost:8000", timeout=10.0) as ac:
        yield ac


@pytest.fixture
async def test_user_data():
    """Provide test user credentials"""
    import random
    # Use random email to avoid conflicts between tests
    random_id = random.randint(1000, 9999)
    return {
        "email": f"testuser{random_id}@example.com",
        "password": "Test@123456"
    }


@pytest.fixture
async def cleanup_test_user(test_user_data):
    """Cleanup test user after test"""
    yield
    
    # Cleanup: Delete test user directly from postgres service (not localhost)
    import asyncpg
    try:
        conn = await asyncpg.connect("postgresql://postgres:postgres123@postgres:5432/trading_signals")
        await conn.execute(
            "DELETE FROM users WHERE email = $1",
            test_user_data["email"]
        )
        await conn.close()
    except Exception as e:
        print(f"Cleanup warning: {e}")
