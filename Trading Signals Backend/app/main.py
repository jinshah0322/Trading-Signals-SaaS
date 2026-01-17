from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import create_db_pool, close_db_pool
from app.redis_client import create_redis_pool, close_redis_pool
from app.routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print(f"Fast API Server is starting up...")
    
    # Initialize database pool
    await create_db_pool()
    
    # Initialize Redis pool
    await create_redis_pool()
    
    print("\nFast API Server is running...")
    
    yield
    
    # Shutdown
    print("Shutting down FAST API Server...")
    
    await close_db_pool()
    await close_redis_pool()
    
    print("FAST API Server has shut down.")
    print("=" * 80 + "\n")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "Trading Signals SaaS API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with connection tests"""
    from app.database import get_pool
    from app.redis_client import get_redis
    
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "redis": "disconnected"
    }
    
    # Check database
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database_error"] = str(e)
    
    # Check Redis
    try:
        redis = get_redis()
        await redis.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["redis_error"] = str(e)
    
    return health_status

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])