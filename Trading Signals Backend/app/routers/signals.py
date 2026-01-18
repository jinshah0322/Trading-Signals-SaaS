from fastapi import APIRouter, Depends
from app.models.signal import SignalsResponse
from app.models.user import UserInDB
from app.services.signal_service import get_signals_for_user
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=SignalsResponse)
async def get_signals(current_user: UserInDB = Depends(get_current_user)):
    """
    Get trading signals based on user's subscription status
    
    Requires valid JWT token in Authorization header
    
    - **Free users**: See 3 signals
    - **Paid users**: See all 20 signals
    
    Signals are cached for 5 minutes for performance
    """
    # Get signals based on user's payment status
    result = await get_signals_for_user(is_paid=current_user.is_paid)
    
    return SignalsResponse(
        signals=result["signals"],
        total=result["total"],
        is_paid=result["is_paid"],
        cached=result["cached"],
        message=result["message"]
    )
