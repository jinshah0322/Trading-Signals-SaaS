from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.database import create_db_pool, close_db_pool
from app.redis_client import create_redis_pool, close_redis_pool
from app.routers import auth_router, billing_router, signals_router


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


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Convert Pydantic validation errors to a consistent format matching HTTPException
    This ensures frontend gets uniform error responses
    """
    # Extract first error message
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = first_error['loc'][-1] if first_error['loc'] else 'unknown'
        message = first_error['msg']
        
        # Custom formatting for cleaner messages
        if field != 'unknown':
            error_message = f"{field.capitalize()}: {message}"
        else:
            error_message = message
    else:
        error_message = "Validation error"
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": error_message}
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
app.include_router(billing_router, prefix="/billing", tags=["Billing"])
app.include_router(signals_router, prefix="/signals", tags=["Trading Signals"])