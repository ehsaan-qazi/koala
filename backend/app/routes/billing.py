import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing"])

def verify_lemonsqueezy_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifies the webhook signature from LemonSqueezy."""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@router.post("/webhook")
async def lemonsqueezy_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles LemonSqueezy webhook events."""
    signature = request.headers.get("X-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    payload = await request.body()
    
    # In development, if secret is empty, we bypass verification
    if settings.lemonsqueezy_webhook_secret:
        if not verify_lemonsqueezy_signature(payload, signature, settings.lemonsqueezy_webhook_secret):
            raise HTTPException(status_code=400, detail="Invalid signature")

    data = await request.json()
    event_name = data.get("meta", {}).get("event_name")
    
    # Extract subscription details
    attributes = data.get("data", {}).get("attributes", {})
    _customer_id = str(attributes.get("customer_id"))
    user_email = attributes.get("user_email")
    provider_sub_id = str(data.get("data", {}).get("id"))
    sub_status = attributes.get("status")
    
    if not user_email:
        # Cannot link to user without email
        return {"status": "ignored", "reason": "No email provided"}

    # Find the user by email
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    
    if not user:
        # User not found, might have deleted account
        return {"status": "ignored", "reason": "User not found"}

    if event_name in ["subscription_created", "subscription_updated"]:
        # Update or create subscription record
        sub_result = await db.execute(select(Subscription).where(Subscription.provider_sub_id == provider_sub_id))
        subscription = sub_result.scalar_one_or_none()
        
        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                provider="lemonsqueezy",
                provider_sub_id=provider_sub_id,
                plan="pro",
                status=sub_status
            )
            db.add(subscription)
        else:
            subscription.status = sub_status
            
        # Parse dates if available
        renews_at = attributes.get("renews_at")
        if renews_at:
            # LemonSqueezy dates are ISO 8601
            try:
                subscription.current_period_end = datetime.fromisoformat(renews_at.replace('Z', '+00:00'))
            except ValueError:
                pass
                
        # Update user's plan based on subscription status
        if sub_status in ["active", "on_trial", "past_due"]:
            user.plan = "pro"
            user.plan_expires_at = subscription.current_period_end
        else:
            user.plan = "free"
            
        await db.commit()
        return {"status": "success", "action": "updated"}

    elif event_name in ["subscription_cancelled", "subscription_expired"]:
        # Subscription ended
        sub_result = await db.execute(select(Subscription).where(Subscription.provider_sub_id == provider_sub_id))
        subscription = sub_result.scalar_one_or_none()
        
        if subscription:
            subscription.status = sub_status
            subscription.cancelled_at = datetime.now()
            
        # Revert user to free plan
        user.plan = "free"
        user.plan_expires_at = None
        
        await db.commit()
        return {"status": "success", "action": "cancelled"}

    return {"status": "ignored", "reason": "Unhandled event type"}

@router.get("/checkout-url")
async def get_checkout_url(current_user: User = Depends(get_current_user)):
    """
    Returns the LemonSqueezy checkout URL for the Pro plan.
    In a real app, you'd use the LemonSqueezy API to generate a checkout session
    with the user's email pre-filled.
    """
    if not settings.lemonsqueezy_store_id or not settings.lemonsqueezy_variant_id:
        # Fallback for dev mode
        return {"checkout_url": "https://example.lemonsqueezy.com/checkout"}
        
    url = f"https://{settings.lemonsqueezy_store_id}.lemonsqueezy.com/checkout/buy/{settings.lemonsqueezy_variant_id}?checkout[email]={current_user.email}"
    return {"checkout_url": url}
