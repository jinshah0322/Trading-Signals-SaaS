from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db_connection
from app.models.user import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user from database by email"""
    async with get_db_connection() as conn:
        query = """
            SELECT id, email, password_hash, is_paid, stripe_customer_id, stripe_subscription_id, created_at, updated_at
            FROM users
            WHERE email = $1
        """
        row = await conn.fetchrow(query, email)
        
        if row:
            return UserInDB(**dict(row))
        return None


async def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """Get user from database by ID"""
    async with get_db_connection() as conn:
        query = """
            SELECT id, email, password_hash, is_paid, stripe_customer_id,stripe_subscription_id, created_at, updated_at
            FROM users
            WHERE id = $1
        """
        row = await conn.fetchrow(query, user_id)
        
        if row:
            return UserInDB(**dict(row))
        return None


async def create_user(email: str, password: str) -> UserInDB:
    """Create new user in database"""
    password_hash = hash_password(password)
    
    async with get_db_connection() as conn:
        query = """
            INSERT INTO users (email, password_hash, is_paid)
            VALUES ($1, $2, $3)
            RETURNING id, email, password_hash, is_paid, stripe_customer_id,stripe_subscription_id, created_at, updated_at
        """
        row = await conn.fetchrow(query, email, password_hash, False)
        
        return UserInDB(**dict(row))


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def update_user_subscription(
    user_id: int,
    stripe_customer_id: str,
    stripe_subscription_id: str
) -> Optional[UserInDB]:
    """Update user's subscription status"""
    async with get_db_connection() as conn:
        query = """
            UPDATE users
            SET is_paid = TRUE,stripe_customer_id = $2,stripe_subscription_id = $3,updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING id, email, password_hash, is_paid, stripe_customer_id,stripe_subscription_id, created_at, updated_at
        """
        row = await conn.fetchrow(query, user_id, stripe_customer_id, stripe_subscription_id)
        
        if row:
            return UserInDB(**dict(row))
        return None