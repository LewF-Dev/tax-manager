"""Stripe integration service."""
import stripe
from typing import Optional

from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_customer(email: str, name: Optional[str] = None) -> str:
    """
    Create a Stripe customer.
    
    Args:
        email: Customer email
        name: Customer name
        
    Returns:
        Stripe customer ID
    """
    customer = stripe.Customer.create(
        email=email,
        name=name,
    )
    return customer.id


def create_checkout_session(
    customer_id: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """
    Create a Stripe Checkout session for subscription.
    
    Args:
        customer_id: Stripe customer ID
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
        
    Returns:
        Checkout session URL
    """
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


def create_customer_portal_session(
    customer_id: str,
    return_url: str,
) -> str:
    """
    Create a Stripe Customer Portal session.
    
    Args:
        customer_id: Stripe customer ID
        return_url: URL to return to after portal
        
    Returns:
        Portal session URL
    """
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def get_subscription_status(subscription_id: str) -> str:
    """
    Get subscription status from Stripe.
    
    Args:
        subscription_id: Stripe subscription ID
        
    Returns:
        Subscription status (active, past_due, canceled, etc.)
    """
    subscription = stripe.Subscription.retrieve(subscription_id)
    return subscription.status


def cancel_subscription(subscription_id: str) -> None:
    """
    Cancel a subscription immediately.
    
    Args:
        subscription_id: Stripe subscription ID
    """
    stripe.Subscription.delete(subscription_id)
