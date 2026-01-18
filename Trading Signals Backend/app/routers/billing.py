from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.models.billing import CheckoutResponse, SubscriptionStatus, WebhookResponse
from app.models.user import UserInDB
from app.services.stripe_service import (
    create_checkout_session,
    verify_webhook_signature,
    is_webhook_processed,
    mark_webhook_processed,
    handle_checkout_completed,
    get_subscription_status
)
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(current_user: UserInDB = Depends(get_current_user)):
    # Check if user is already paid
    if current_user.is_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription"
        )
    
    # Create checkout session
    checkout_data = await create_checkout_session(
        user_id=current_user.id,
        user_email=current_user.email
    )
    
    return CheckoutResponse(
        checkout_url=checkout_data['checkout_url'],
        session_id=checkout_data['session_id']
    )


@router.get("/status", response_model=SubscriptionStatus)
async def get_billing_status(current_user: UserInDB = Depends(get_current_user)):
    status_data = await get_subscription_status(current_user.id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SubscriptionStatus(**status_data)


@router.post("/webhooks/stripe", response_model=WebhookResponse)
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint to receive payment events
    
    This endpoint is called by Stripe when payment events occur.
    It verifies the webhook signature and processes the event.
    
    Events handled:
    - checkout.session.completed: When payment is successful
    
    Note: This endpoint is NOT protected by JWT (Stripe calls it)
    """
    # Get raw body and signature
    payload = await request.body()
    signature = request.headers.get('stripe-signature')
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    # Verify webhook signature
    event = verify_webhook_signature(payload, signature)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    # Get event type and ID
    event_type = event['type']
    event_id = event['id']
    
    print(f"Received Stripe webhook: {event_type} (ID: {event_id})")
    
    # Check idempotency - have we already processed this event?
    if await is_webhook_processed(event_id):
        print(f"Event {event_id} already processed (idempotent)")
        return WebhookResponse(
            status="success",
            message="Event already processed"
        )
    
    # Handle different event types
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        
        # Check if payment was successful
        payment_status = session.get('payment_status')
        
        if payment_status == 'paid':
            # Update user subscription
            success = await handle_checkout_completed(session)
            
            if success:
                # Mark webhook as processed
                await mark_webhook_processed(event_id)
                
                return WebhookResponse(
                    status="success",
                    message="User subscription updated"
                )
            else:
                return WebhookResponse(
                    status="error",
                    message="Failed to update user"
                )
        else:
            print(f"Payment not completed: {payment_status}")
            return WebhookResponse(
                status="ignored",
                message=f"Payment status: {payment_status}"
            )
    
    else:
        # Other event types (we don't handle them for now)
        print(f"Unhandled event type: {event_type}")
        return WebhookResponse(
            status="ignored",
            message=f"Event type {event_type} not handled"
        )