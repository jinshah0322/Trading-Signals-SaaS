from fastapi import APIRouter, HTTPException, status, Depends
from app.models.auth import SignupRequest, LoginRequest, LoginResponse
from app.models.user import UserResponse, UserInDB
from app.services.auth_service import (
    get_user_by_email,
    create_user,
    authenticate_user,
    create_access_token
)
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    # Check if user already exists
    existing_user = await get_user_by_email(request.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await create_user(request.email, request.password)
    
    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "is_paid": user.is_paid
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "is_paid": user.is_paid,
            "created_at": user.created_at.isoformat()
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Authenticate user
    user = await authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "is_paid": user.is_paid
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "is_paid": user.is_paid,
            "created_at": user.created_at.isoformat()
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current authenticated user's information which Requires valid JWT token in Authorization header
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_paid=current_user.is_paid,
        created_at=current_user.created_at
    )