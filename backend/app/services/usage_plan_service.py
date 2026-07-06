"""User plan and OCR quota helpers."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import UserUsagePlan


PLAN_LABELS = {
    "default": "默认套餐",
    "free_seed": "种子免费终身",
    "seed_lifetime_9_9": "9.9 种子终身",
    "manual_trial": "人工试用",
    "standard": "标准套餐",
    "custom": "自定义套餐",
}


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _active_plan(profile: UserUsagePlan | None) -> UserUsagePlan | None:
    if not profile or profile.status != "active":
        return None
    now = datetime.now()
    if profile.starts_at and profile.starts_at > now:
        return None
    if profile.expires_at and profile.expires_at <= now:
        return None
    return profile


async def get_user_usage_plan(db: AsyncSession, user_id: str) -> UserUsagePlan | None:
    return (
        await db.execute(select(UserUsagePlan).where(UserUsagePlan.user_id == user_id))
    ).scalar_one_or_none()


async def get_effective_ocr_quota_limits(db: AsyncSession, user_id: str) -> dict:
    profile = await get_user_usage_plan(db, user_id)
    active_profile = _active_plan(profile)

    daily_limit = max(int(settings.OCR_DAILY_USER_LIMIT or 0), 0)
    monthly_limit = 0
    source = "environment_default"

    if active_profile:
        source = "user_usage_plan"
        if active_profile.daily_ocr_limit is not None:
            daily_limit = max(int(active_profile.daily_ocr_limit or 0), 0)
        if active_profile.monthly_ocr_limit is not None:
            monthly_limit = max(int(active_profile.monthly_ocr_limit or 0), 0)

    return {
        "plan_code": profile.plan_code if profile else "default",
        "plan_name": (
            profile.plan_name
            if profile and profile.plan_name
            else PLAN_LABELS.get(profile.plan_code if profile else "default", "默认套餐")
        ),
        "daily_limit": daily_limit,
        "monthly_limit": monthly_limit,
        "source": source,
        "profile": profile,
    }


def serialize_user_usage_plan(profile: UserUsagePlan | None, limits: dict | None = None) -> dict:
    if limits is None:
        limits = {}
    plan_code = profile.plan_code if profile else "default"
    return {
        "id": profile.id if profile else None,
        "user_id": profile.user_id if profile else None,
        "plan_code": plan_code,
        "plan_name": (profile.plan_name if profile and profile.plan_name else PLAN_LABELS.get(plan_code, "默认套餐")),
        "daily_ocr_limit": profile.daily_ocr_limit if profile else None,
        "monthly_ocr_limit": profile.monthly_ocr_limit if profile else None,
        "effective_daily_ocr_limit": limits.get("daily_limit"),
        "effective_monthly_ocr_limit": limits.get("monthly_limit"),
        "status": profile.status if profile else "active",
        "source": profile.source if profile else "environment_default",
        "starts_at": _iso_or_none(profile.starts_at) if profile else None,
        "expires_at": _iso_or_none(profile.expires_at) if profile else None,
        "notes": profile.notes if profile else None,
        "created_at": _iso_or_none(profile.created_at) if profile else None,
        "updated_at": _iso_or_none(profile.updated_at) if profile else None,
    }


async def upsert_user_usage_plan(db: AsyncSession, user_id: str, values: dict[str, Any]) -> UserUsagePlan:
    profile = await get_user_usage_plan(db, user_id)
    if not profile:
        profile = UserUsagePlan(user_id=user_id)
        db.add(profile)

    for field, value in values.items():
        setattr(profile, field, value)

    if not profile.plan_name:
        profile.plan_name = PLAN_LABELS.get(profile.plan_code, "自定义套餐")
    if not profile.source:
        profile.source = "manual"
    if not profile.status:
        profile.status = "active"

    await db.flush()
    return profile
