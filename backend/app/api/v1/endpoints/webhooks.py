from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import Subscription
from app.core.config import get_settings
from app.core.deps import get_current_user
import json
from datetime import datetime
from uuid import UUID

router = APIRouter()
settings = get_settings()

# Try to import stripe (optional - only needed for production)
try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    Stripe must be configured for this to work.
    """
    if not settings.STRIPE_SECRET_KEY or not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    body = await request.body()
    sig = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            body, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        
        if user_id:
            result = await db.execute(
                select(Subscription).where(Subscription.user_id == UUID(user_id))
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                subscription.plan_type = session.get("metadata", {}).get("plan_type", "personal")
                subscription.status = "active"
                subscription.stripe_subscription_id = session.get("subscription")
                subscription.current_period_start = datetime.utcnow()
                if session.get("metadata", {}).get("interval") == "year":
                    from datetime import timedelta
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=365)
                else:
                    from datetime import timedelta
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
                
                await db.commit()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription_obj = event["data"]["object"]
        stripe_sub_id = subscription_obj.get("id")
        
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "cancelled"
            subscription.plan_type = "free"
            await db.commit()
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_sub_id = invoice.get("subscription")
        
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_sub_id
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "expired"
            await db.commit()
    
    return {"status": "success"}


@router.post("/revenuecat")
async def revenuecat_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle RevenueCat webhook events for subscription sync.
    RevenueCat must be configured for this to work.
    """
    if not settings.REVENUECAT_API_KEY:
        raise HTTPException(status_code=503, detail="RevenueCat not configured")
    
    body = await request.json()
    
    event_type = body.get("event", {}).get("type")
    
    if event_type in ["subscription_initial_purchase", "subscription_renewed"]:
        app_user_id = body.get("app_user_id")
        
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == UUID(app_user_id))
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "active"
            await db.commit()
    
    elif event_type in ["subscription_cancelled", "subscription_expired"]:
        app_user_id = body.get("app_user_id")
        
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == UUID(app_user_id))
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "cancelled"
            subscription.plan_type = "free"
            await db.commit()
    
    return {"status": "success"}