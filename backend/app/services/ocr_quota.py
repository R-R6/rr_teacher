"""
Daily quota controls for paid OCR engines.
"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import OcrUsageLog

COUNTED_STATUSES = {"reserved", "completed", "failed"}


def paid_ocr_engines() -> set[str]:
    return {
        item.strip().lower()
        for item in (settings.OCR_PAID_ENGINES or "").split(",")
        if item.strip()
    }


def is_paid_ocr_engine(engine: str) -> bool:
    return (engine or "").lower() in paid_ocr_engines()


def _today() -> str:
    return datetime.now().date().isoformat()


def _is_user_exceeded(status: dict) -> bool:
    limit = int(status.get("limit") or 0)
    return limit > 0 and int(status.get("used") or 0) > limit


def _is_global_exceeded(status: dict) -> bool:
    limit = int(status.get("global_limit") or 0)
    return limit > 0 and int(status.get("global_used") or 0) > limit


async def _count_usage(
    db: AsyncSession,
    engine: str,
    day: str,
    user_id: str | None = None,
) -> int:
    stmt = select(func.count()).select_from(OcrUsageLog).where(
        OcrUsageLog.engine == engine,
        OcrUsageLog.usage_day == day,
        OcrUsageLog.status.in_(COUNTED_STATUSES),
    )
    if user_id:
        stmt = stmt.where(OcrUsageLog.user_id == user_id)
    return int((await db.execute(stmt)).scalar() or 0)


async def get_ocr_quota_status(db: AsyncSession, user_id: str, engine: str) -> dict:
    engine = (engine or "").lower()
    if not is_paid_ocr_engine(engine):
        return {"limited": False}

    day = _today()
    user_limit = max(int(settings.OCR_DAILY_USER_LIMIT or 0), 0)
    global_limit = max(int(settings.OCR_DAILY_GLOBAL_LIMIT or 0), 0)
    user_used = await _count_usage(db, engine, day, user_id=user_id)
    global_used = await _count_usage(db, engine, day)

    user_remaining = None if user_limit == 0 else max(user_limit - user_used, 0)
    global_remaining = None if global_limit == 0 else max(global_limit - global_used, 0)
    limited = (user_remaining == 0) or (global_remaining == 0)
    message = ""
    if limited:
        message = "今日高精度 OCR 额度已用完，请切换极速识别或明天再试"

    return {
        "limited": limited,
        "used": user_used,
        "limit": user_limit,
        "remaining": user_remaining,
        "global_used": global_used,
        "global_limit": global_limit,
        "global_remaining": global_remaining,
        "message": message,
    }


async def reserve_ocr_quota(db: AsyncSession, user_id: str, engine: str) -> str | None:
    if not is_paid_ocr_engine(engine):
        return None

    log = OcrUsageLog(
        user_id=user_id,
        engine=engine,
        usage_day=_today(),
        status="reserved",
    )
    db.add(log)
    await db.flush()
    await db.commit()

    status = await get_ocr_quota_status(db, user_id, engine)
    if _is_user_exceeded(status) or _is_global_exceeded(status):
        await finalize_ocr_quota(db, log.id, success=False, counted_failure=False)
        raise HTTPException(status_code=429, detail=status["message"])

    return log.id


async def finalize_ocr_quota(
    db: AsyncSession,
    quota_log_id: str | None,
    success: bool,
    error_message: str | None = None,
    counted_failure: bool = True,
) -> None:
    if not quota_log_id:
        return
    log = await db.get(OcrUsageLog, quota_log_id)
    if not log:
        return
    log.status = "completed" if success else ("failed" if counted_failure else "cancelled")
    log.error_message = error_message[:1000] if error_message else None
    await db.flush()
    await db.commit()
