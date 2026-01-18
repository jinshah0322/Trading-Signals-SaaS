import stripe
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.config import settings
from app.services.auth_service import update_user_subscription, get_user_by_id
from app.redis_client import get_redis

stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_checkout_session(user_id: int, user_email: str) -> Dict[str, str]:
    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                }
            ],
            mode='payment',  # One-time payment
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
            metadata={
                'user_id': str(user_id),  # Store user_id in metadata
            }
        )
        
        return {
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )

def verify_webhook_signature(payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
    """Verify Stripe webhook signature and return event object if valid"""
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    
    except stripe.error.SignatureVerificationError:
        return None
    except Exception:
        return None


async def is_webhook_processed(event_id: str) -> bool:
    """Check if webhook event has already been processed (idempotency)"""
    redis = get_redis()
    redis_key = f"webhook:{event_id}"
    
    result = await redis.get(redis_key)
    return result is not None


async def mark_webhook_processed(event_id: str) -> None:
    """Mark webhook event as processed in Redis"""
    redis = get_redis()
    redis_key = f"webhook:{event_id}"
    
    # Store for 24 hours (86400 seconds)
    await redis.setex(redis_key, 86400, "processed")


async def handle_checkout_completed(session: Dict[str, Any]) -> bool:
    """
    Handle successful checkout completion
    
    Args:
        session: Stripe checkout session object
    
    Returns:
        True if user updated successfully
    """
    # Extract user_id from metadata
    user_id = session.get('metadata', {}).get('user_id')
    
    if not user_id:
        print(f"No user_id in session metadata: {session.get('id')}")
        return False
    
    user_id = int(user_id)
    
    # Get Stripe customer and payment intent
    customer_id = session.get('customer')
    payment_intent = session.get('payment_intent')
    
    # Create a subscription ID (for one-time payment, we use payment_intent as reference)
    subscription_id = payment_intent or session.get('id')
    
    # Update user in database
    try:
        updated_user = await update_user_subscription(
            user_id=user_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id
        )
        
        if updated_user:
            print(f"User {user_id} ({updated_user.email}) marked as PAID")
            return True
        else:
            print(f"Failed to update user {user_id}")
            return False
    
    except Exception as e:
        print(f"Error updating user {user_id}: {str(e)}")
        return False

async def get_subscription_status(user_id: int) -> Optional[Dict[str, Any]]:
    user = await get_user_by_id(user_id)
    
    if not user:
        return None
    
    return {
        'is_paid': user.is_paid,
        'stripe_customer_id': user.stripe_customer_id,
        'stripe_subscription_id': user.stripe_subscription_id,
        'email': user.email
    }