import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from app.config import settings


# Global connection pool
db_pool: Optional[asyncpg.Pool] = None


async def create_db_pool():
    """Create database connection pool"""
    global db_pool
    
    db_url = settings.DATABASE_URL
    
    db_pool = await asyncpg.create_pool(
        db_url,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
        command_timeout=60
    )
    
    print(f"Database pool created (min={settings.DB_POOL_MIN_SIZE}, max={settings.DB_POOL_MAX_SIZE})")
    return db_pool


async def close_db_pool():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("Database pool closed")


def get_pool() -> asyncpg.Pool:
    """Get the database connection pool"""
    if db_pool is None:
        raise RuntimeError("Database pool not initialized. Call create_db_pool() first.")
    return db_pool


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for getting a database connection from pool
    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    """
    pool = get_pool()
    async with pool.acquire() as connection:
        yield connection