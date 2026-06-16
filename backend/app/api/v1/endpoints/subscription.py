from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import User, Subscription
from app.schemas.schemas import (
    SubscriptionCreateRequest, SubscriptionResponse, SubscriptionStatusResponse
)
from app.core.deps import get_current_user
from app.core.config import get_settings
from datetime import datetime, timedelta
import uuid

router = APIRouter()
settings = get_settings()

# Stripe price IDs (created via Stripe Dashboard or API)
STRIPE_PRICE_IDS = {
    "personal_monthly": "price_1ThEhURyllpyRyqfsiQK2qEt",
    "personal_yearly": "price_1ThEhURyllpyRyqfGpfQAH26",
    "family_monthly": "price_1ThEhVRyllpyRyqfJENZWCSE",
    "family_yearly": "price_1ThEhVRyllpyRyqfRkwYq3D0",
}

# Try to import stripe
try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False


def calculate_trial_days_remaining(subscription: Subscription) -> int:
    """Calculate remaining trial days based on trial_end_date."""
    if not subscription.trial_end_date:
        return 0
    now = datetime.utcnow()
    if subscription.trial_end_date > now:
        delta = subscription.trial_end_date - now
        return max(0, delta.days)
    return 0


@router.post("/create")
async def create_subscription(
    data: SubscriptionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe checkout session for subscription.
    If Stripe is not configured, creates a mock subscription with 7-day free trial.
    """
    # Get or create subscription record
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            plan_type="free",
            status="active"
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    # If already on paid plan, don't allow re-subscription
    if subscription.plan_type != "free" and subscription.status == "active":
        raise HTTPException(status_code=400, detail="Already on an active subscription")

    # Mock mode: If Stripe not configured, simulate subscription with 7-day trial
    if not STRIPE_AVAILABLE or not settings.STRIPE_SECRET_KEY:
        # Calculate trial period
        now = datetime.utcnow()
        trial_end = now + timedelta(days=7)

        # Determine period end based on interval
        interval = data.interval or "month"
        period_end = trial_end + timedelta(days=30) if interval == "month" else trial_end + timedelta(days=365)

        subscription.plan_type = data.plan_type
        subscription.status = "trialing"  # Special status for trial period
        subscription.trial_end_date = trial_end
        subscription.current_period_start = now
        subscription.current_period_end = period_end
        subscription.stripe_subscription_id = f"mock_{uuid.uuid4().hex[:12]}"

        await db.commit()
        await db.refresh(subscription)

        return {
            "checkout_url": None,  # No redirect needed in mock mode
            "session_id": subscription.stripe_subscription_id,
            "mock_mode": True,
            "trial_end_date": trial_end.isoformat(),
            "message": "7-day free trial activated! You will not be charged until the trial ends."
        }

    # Real Stripe checkout
    interval = data.interval or "month"
    # Map interval to suffix: "month" -> "monthly", "year" -> "yearly"
    interval_suffix = "yearly" if interval == "year" else "monthly"
    price_key = f"{data.plan_type}_{interval_suffix}"
    price_id = STRIPE_PRICE_IDS.get(price_key)

    if not price_id:
        raise HTTPException(status_code=400, detail=f"Invalid plan type or interval: {price_key}")

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": price_id,
            "quantity": 1
        }],
        customer_email=current_user.email,
        metadata={
            "user_id": str(current_user.id),
            "plan_type": data.plan_type,
            "interval": interval
        },
        success_url=f"http://localhost:8000/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"http://localhost:8000/subscription/canceled"
    )

    return {
        "checkout_url": checkout_session.url,
        "session_id": checkout_session.id
    }


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel current subscription via Stripe."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    if subscription.plan_type == "free":
        raise HTTPException(status_code=400, detail="Already on free plan")

    # Cancel in Stripe if we have subscription ID
    if STRIPE_AVAILABLE and subscription.stripe_subscription_id:
        try:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        except Exception:
            pass  # Continue even if Stripe call fails

    subscription.plan_type = "free"
    subscription.status = "cancelled"
    subscription.updated_at = datetime.utcnow()
    subscription.trial_end_date = None

    await db.commit()
    await db.refresh(subscription)

    return subscription


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            plan_type="free",
            status="active"
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    # is_active: true if on paid plan with active/trialing status
    is_active = subscription.status in ("active", "trialing") and subscription.plan_type != "free"

    # Calculate trial days remaining
    trial_days_remaining = calculate_trial_days_remaining(subscription)

    return SubscriptionStatusResponse(
        subscription=subscription,
        plan_type=subscription.plan_type,
        is_active=is_active,
        current_period_end=subscription.current_period_end,
        trial_days_remaining=trial_days_remaining
    )


@router.get("/portal")
async def get_stripe_portal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Stripe billing portal session URL."""
    if not STRIPE_AVAILABLE or not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No Stripe customer found")

    session = stripe.billing_portal.Session.create(
        customer=subscription.stripe_customer_id,
        return_url="http://localhost:8000"
    )

    return {"portal_url": session.url}


@router.get("/success")
async def subscription_success(
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Handle successful Stripe checkout - update subscription status."""
    if not STRIPE_AVAILABLE:
        return {"status": "stripe_not_available"}

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        user_id = checkout_session.metadata.get("user_id")

        if user_id:
            result = await db.execute(
                select(Subscription).where(Subscription.user_id == uuid.UUID(user_id))
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.status = "active"
                subscription.plan_type = checkout_session.metadata.get("plan_type", "personal")
                subscription.stripe_customer_id = checkout_session.customer
                subscription.stripe_subscription_id = checkout_session.subscription
                await db.commit()

        return {"status": "success", "plan": checkout_session.metadata.get("plan_type")}
    except Exception as e:
        return {"status": "error", "message": str(e)}
