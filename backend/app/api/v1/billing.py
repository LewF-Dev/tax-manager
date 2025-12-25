"""Billing and subscription endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import stripe

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.core.config import settings
from app.services.stripe_service import (
    create_customer,
    create_checkout_session,
    create_customer_portal_session,
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/create-checkout-session")
async def create_checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for subscription."""
    # Create Stripe customer if doesn't exist
    if not current_user.stripe_customer_id:
        customer_id = create_customer(
            email=current_user.email,
            name=current_user.full_name,
        )
        current_user.stripe_customer_id = customer_id
        db.commit()
    
    # Create checkout session
    checkout_url = create_checkout_session(
        customer_id=current_user.stripe_customer_id,
        success_url=f"{settings.CORS_ORIGINS[0]}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.CORS_ORIGINS[0]}/pricing",
    )
    
    return {"checkout_url": checkout_url}


@router.post("/create-portal-session")
async def create_portal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Customer Portal session."""
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found",
        )
    
    portal_url = create_customer_portal_session(
        customer_id=current_user.stripe_customer_id,
        return_url=f"{settings.CORS_ORIGINS[0]}/settings",
    )
    
    return {"portal_url": portal_url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handle Stripe webhook events.
    
    Updates subscription status based on Stripe events.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session["customer"]
        subscription_id = session["subscription"]
        
        # Update user subscription
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_id = subscription_id
            user.subscription_status = "active"
            db.commit()
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        status_value = subscription["status"]
        
        # Update subscription status
        user = db.query(User).filter(User.subscription_id == subscription_id).first()
        if user:
            user.subscription_status = status_value
            db.commit()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        
        # Mark subscription as canceled
        user = db.query(User).filter(User.subscription_id == subscription_id).first()
        if user:
            user.subscription_status = "canceled"
            db.commit()
    
    return {"status": "success"}
