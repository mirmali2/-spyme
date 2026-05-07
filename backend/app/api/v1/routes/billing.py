from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.subscription import Subscription
from app.services.billing import PLANS, create_checkout_session, plan_period_end, trial_period_end
from app.utils.auth import current_user

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str  # monthly | yearly
    success_url: str = "spyme://billing/success"
    cancel_url: str = "spyme://billing/cancel"


class SubscriptionStatus(BaseModel):
    plan: str
    status: str
    current_period_end: datetime
    days_remaining: int
    is_pro: bool
    is_trial: bool


@router.get("/plans")
async def list_plans():
    """Public — show all plans on the paywall screen."""
    return {
        plan_id: {
            "id": plan_id,
            "name": p["name"],
            "price_cents": p["price_cents"],
            "price_display": f"${p['price_cents'] / 100:.2f}",
            "duration_days": p["duration_days"],
            "features": p["features"],
            "savings_cents": p.get("savings_cents", 0),
        }
        for plan_id, p in PLANS.items()
    }


@router.get("/me", response_model=SubscriptionStatus)
async def my_subscription(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not sub:
        # Auto-create trial if missing (race condition safety)
        sub = Subscription(user_id=user.id, plan="trial", status="active",
                           current_period_end=trial_period_end())
        db.add(sub)
        await db.commit()
        await db.refresh(sub)

    end = sub.current_period_end
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if sub.status == "active" and end < now:
        sub.status = "expired"
        await db.commit()

    days_left = max(0, (end - now).days)
    return SubscriptionStatus(
        plan=sub.plan,
        status=sub.status,
        current_period_end=sub.current_period_end,
        days_remaining=days_left,
        is_pro=(sub.status == "active" and sub.plan in {"monthly", "yearly"}),
        is_trial=(sub.status == "active" and sub.plan == "trial"),
    )


@router.post("/checkout")
async def start_checkout(body: CheckoutRequest, user=Depends(current_user)):
    """Returns a Stripe checkout URL the mobile app opens in a webview."""
    if body.plan not in {"monthly", "yearly"}:
        raise HTTPException(400, "Invalid plan")
    return create_checkout_session(
        plan=body.plan,
        user_email=user.email,
        user_id=str(user.id),
        success_url=body.success_url,
        cancel_url=body.cancel_url,
    )


@router.post("/dev-upgrade")
async def dev_upgrade(plan: str, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """DEV ONLY — instantly upgrade without Stripe. Remove in production."""
    if plan not in {"monthly", "yearly"}:
        raise HTTPException(400, "Invalid plan")
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not sub:
        sub = Subscription(user_id=user.id)
        db.add(sub)
    sub.plan = plan
    sub.status = "active"
    sub.current_period_end = plan_period_end(plan)
    await db.commit()
    return {"ok": True, "plan": plan, "ends": sub.current_period_end}
