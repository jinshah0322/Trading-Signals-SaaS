from pydantic import BaseModel
from typing import Optional


class CheckoutRequest(BaseModel):
    """No body needed use JWT to identify user"""
    pass


class CheckoutResponse(BaseModel):
    """Response model for checkout session"""
    checkout_url: str
    session_id: str


class SubscriptionStatus(BaseModel):
    """Response model for subscription status"""
    is_paid: bool
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    email: str


class WebhookResponse(BaseModel):
    """Response model for webhook endpoint"""
    status: str
    message: Optional[str] = None