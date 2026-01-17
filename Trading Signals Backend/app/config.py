from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "Trading Signals SaaS"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    DB_POOL_MIN_SIZE: int = 10
    DB_POOL_MAX_SIZE: int = 20
    
    # Redis
    REDIS_URL: str
    REDIS_POOL_MAX_CONNECTIONS: int = 50
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID: str
    
    # Frontend
    FRONTEND_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()