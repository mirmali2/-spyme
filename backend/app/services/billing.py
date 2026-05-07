"""Subscription plans + Stripe checkout. Stripe is lazy-imported."""
from datetime import datetime, timedelta, timezone

from app.core.config import settings

MAX_DEVICES_GLOBAL = 4   # hard cap — no plan exceeds this

PLANS = {
    "trial": {
        "name": "Free Trial",
        "price_cents": 0,
        "duration_days": 2,
        "device_limit": 4,
        "features": [
            "Up to 4 laptop cameras",
            "Live view + push alerts",
            "Person + motion + theft AI",
            "Fire alerts + SMS + siren",
            "All Pro features for 2 days",
        ],
    },
    "free": {
        "name": "Free",
        "price_cents": 0,
        "duration_days": 0,  # forever
        "device_limit": 1,
        "features": [
            "1 laptop camera",
            "Live view + push alerts",
            "Person + motion detection",
            "24-hour event history",
        ],
    },
    "monthly": {
        "name": "SPYME Pro",
        "price_cents": 1000,
        "duration_days": 30,
        "device_limit": 4,
        "stripe_price_id_env": "STRIPE_PRICE_MONTHLY",
        "features": [
            "Up to 4 laptop cameras",
            "30-day event history",
            "Multi-person + theft AI",
            "🔥 Fire alerts + SMS + siren",
            "Apple Watch app",
            "Store clips in your Google Drive",
            "Priority support",
        ],
    },
    "yearly": {
        "name": "SPYME Pro (Yearly)",
        "price_cents": 10000,
        "duration_days": 365,
        "device_limit": 4,
        "savings_cents": 2000,  # 12*$10 - $100 = $20 saved
        "stripe_price_id_env": "STRIPE_PRICE_YEARLY",
        "features": [
            "Everything in Pro Monthly",
            "Up to 4 laptop cameras",
            "Save $20 vs monthly billing",
            "Locked-in price for 12 months",
        ],
    },
}


def device_limit_for(plan: str, status: str) -> int:
    """How many devices a user can register based on their current plan + status."""
    if status != "active":
        return PLANS["free"]["device_limit"]
    p = PLANS.get(plan, PLANS["free"])
    return min(p.get("device_limit", 1), MAX_DEVICES_GLOBAL)


def trial_period_end() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=PLANS["trial"]["duration_days"])


def plan_period_end(plan: str) -> datetime:
    days = PLANS[plan]["duration_days"]
    return datetime.now(timezone.utc) + timedelta(days=days)


def create_checkout_session(plan: str, user_email: str, user_id: str, success_url: str, cancel_url: str) -> dict:
    """Create a Stripe Checkout session. Falls back to dev URL if Stripe not configured."""
    if plan not in {"monthly", "yearly"}:
        raise ValueError(f"Plan {plan} is not purchasable")

    sk = getattr(settings, "STRIPE_SECRET_KEY", "")
    price_id = getattr(settings, PLANS[plan]["stripe_price_id_env"], "")
    if not (sk and price_id):
        # Dev mode — return a fake checkout URL
        return {
            "checkout_url": f"{success_url}?dev_mode=true&plan={plan}",
            "session_id": f"cs_dev_{plan}_{user_id[:8]}",
        }

    import stripe
    stripe.api_key = sk
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=user_email,
        client_reference_id=user_id,
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={"plan": plan, "user_id": user_id},
    )
    return {"checkout_url": session.url, "session_id": session.id}
