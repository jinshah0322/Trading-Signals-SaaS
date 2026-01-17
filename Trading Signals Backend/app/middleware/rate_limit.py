"""
Rate limiting middleware using Redis
"""
from functools import wraps
from fastapi import Request, HTTPException, status
from typing import Callable
import inspect
from app.services.redis_service import check_rate_limit


def rate_limit(
    key_prefix: str,
    max_requests: int,
    window_seconds: int,
    identifier: str = "ip"
):
    """
    Rate limiting decorator for FastAPI routes
    
    Args:
        key_prefix: Prefix for Redis key (e.g., "login", "signup")
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        identifier: What to use as identifier - "ip" or "email"
    
    Usage:
        @router.post("/login")
        @rate_limit(key_prefix="login", max_requests=5, window_seconds=900, identifier="email")
        async def login(request: Request, data: LoginRequest):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get function signature to find Request parameter
            sig = inspect.signature(func)
            
            request: Request = None
            request_data = None
            
            # Bind arguments to parameters
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Find Request object
            for param_name, param_value in bound_args.arguments.items():
                if isinstance(param_value, Request):
                    request = param_value
                    break
            
            if request is None:
                raise RuntimeError("Request parameter not found in route handler")
            
            # Build rate limit key based on identifier
            if identifier == "ip":
                client_ip = request.client.host
                rate_limit_key = f"rate_limit:{key_prefix}:{client_ip}"
            
            elif identifier == "email":
                # Find request data with email field
                for param_name, param_value in bound_args.arguments.items():
                    if hasattr(param_value, 'email'):
                        request_data = param_value
                        break
                
                if request_data is None or not hasattr(request_data, 'email'):
                    raise RuntimeError("Email not found in request data")
                
                rate_limit_key = f"rate_limit:{key_prefix}:{request_data.email}"
            
            else:
                raise ValueError(f"Invalid identifier: {identifier}")
            
            # Check rate limit
            allowed = await check_rate_limit(rate_limit_key, max_requests, window_seconds)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later."
                )
            
            # Call the actual route handler
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator