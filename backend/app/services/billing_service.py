"""Seed offer billing service."""

from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import (
    BillingEligibility,
    BillingEntitlement,
    BillingEventLog,
    BillingOffer,
    BillingOrder,
    User,
    gen_uuid,
)
from app.services.usage_plan_service import PLAN_LABELS, upsert_user_usage_plan
from app.services.wechat_pay_v3 import WechatPayConfigError, create_jsapi_payment_params


SEED_OFFER_CODE = "seed_2026_round_1"
SEED_OFFER_NAME = "种子计划 · 终身权益"
SEED_PRODUCT_TYPE = "seed_paid_lifetime"
CHANNEL_WECHAT_MINIAPP = "wechat_miniapp"
ENTITLEMENT_LIFETIME = "lifetime_access"

FREE_ELIGIBILITY = "free_seed"
PAID_ELIGIBILITY = "paid_seed_9_9"
ACTIVE_ELIGIBILITY_STATUSES = {"locked", "converted"}
PAYABLE_ORDER_STATUSES = {"pending", "paid"}


def _now() -> datetime:
    return datetime.now()


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _order_no() -> str:
    return f"B{_now().strftime('%Y%m%d%H%M%S')}{gen_uuid()[:8]}"


async def log_billing_event(
    db: AsyncSession,
    event_type: str,
    *,
    user_id: str | None = None,
    offer_id: str | None = None,
    eligibility_id: str | None = None,
    order_id: str | None = None,
    entitlement_id: str | None = None,
    payload: dict | None = None,
) -> None:
    db.add(
        BillingEventLog(
            user_id=user_id,
            offer_id=offer_id,
            eligibility_id=eligibility_id,
            order_id=order_id,
            entitlement_id=entitlement_id,
            event_type=event_type,
            payload=payload or {},
        )
    )


async def get_or_create_seed_offer(db: AsyncSession) -> BillingOffer:
    offer = (
        await db.execute(select(BillingOffer).where(BillingOffer.code == SEED_OFFER_CODE))
    ).scalar_one_or_none()
    if offer:
        return offer

    offer = BillingOffer(
        code=SEED_OFFER_CODE,
        name=SEED_OFFER_NAME,
        status="active",
        free_total=10,
        paid_total=40,
        amount_cents=990,
        currency="CNY",
        payment_window_minutes=30,
    )
    db.add(offer)
    await db.flush()
    await log_billing_event(db, "offer_created", offer_id=offer.id)
    return offer


async def lock_seed_offer(db: AsyncSession) -> BillingOffer:
    offer = await get_or_create_seed_offer(db)
    locked_offer = (
        await db.execute(select(BillingOffer).where(BillingOffer.id == offer.id).with_for_update())
    ).scalar_one_or_none()
    return locked_offer or offer


def serialize_offer(offer: BillingOffer, *, status: str | None = None) -> dict:
    return {
        "id": offer.id,
        "code": offer.code,
        "name": offer.name,
        "status": status or offer.status,
        "free_total": int(offer.free_total or 0),
        "paid_total": int(offer.paid_total or 0),
        "payment_window_minutes": int(offer.payment_window_minutes or 0),
        "price_amount": int(offer.amount_cents or 0),
        "amount_cents": int(offer.amount_cents or 0),
        "currency": offer.currency,
        "starts_at": _iso(offer.starts_at),
        "ends_at": _iso(offer.ends_at),
        "created_at": _iso(offer.created_at),
        "updated_at": _iso(offer.updated_at),
    }


def serialize_eligibility(eligibility: BillingEligibility | None) -> dict | None:
    if not eligibility:
        return None
    return {
        "id": eligibility.id,
        "offer_id": eligibility.offer_id,
        "user_id": eligibility.user_id,
        "type": eligibility.type,
        "status": eligibility.status,
        "slot_no": eligibility.slot_no,
        "expires_at": _iso(eligibility.expires_at),
        "converted_at": _iso(eligibility.converted_at),
        "created_at": _iso(eligibility.created_at),
        "updated_at": _iso(eligibility.updated_at),
    }


def serialize_order(order: BillingOrder | None) -> dict | None:
    if not order:
        return None
    return {
        "id": order.id,
        "order_id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "offer_id": order.offer_id,
        "eligibility_id": order.eligibility_id,
        "product_type": order.product_type,
        "channel": order.channel,
        "status": order.status,
        "amount_total": int(order.amount_total or 0),
        "currency": order.currency,
        "transaction_id": order.transaction_id,
        "payment_params": order.payment_params,
        "expires_at": _iso(order.expires_at),
        "paid_at": _iso(order.paid_at),
        "created_at": _iso(order.created_at),
        "updated_at": _iso(order.updated_at),
    }


def serialize_entitlement(entitlement: BillingEntitlement | None) -> dict | None:
    if not entitlement:
        return None
    return {
        "id": entitlement.id,
        "user_id": entitlement.user_id,
        "offer_id": entitlement.offer_id,
        "eligibility_id": entitlement.eligibility_id,
        "order_id": entitlement.order_id,
        "type": entitlement.type,
        "status": entitlement.status,
        "active": entitlement.status == "active",
        "source": entitlement.source,
        "starts_at": _iso(entitlement.starts_at),
        "expires_at": _iso(entitlement.expires_at),
        "created_at": _iso(entitlement.created_at),
        "updated_at": _iso(entitlement.updated_at),
    }


async def expire_stale_paid_reservations(db: AsyncSession, offer: BillingOffer) -> None:
    now = _now()
    stale_eligibilities = (
        await db.execute(
            select(BillingEligibility).where(
                BillingEligibility.offer_id == offer.id,
                BillingEligibility.type == PAID_ELIGIBILITY,
                BillingEligibility.status == "locked",
                BillingEligibility.expires_at.is_not(None),
                BillingEligibility.expires_at <= now,
            )
        )
    ).scalars().all()

    for eligibility in stale_eligibilities:
        eligibility.status = "expired"
        eligibility.updated_at = now
        orders = (
            await db.execute(
                select(BillingOrder).where(
                    BillingOrder.eligibility_id == eligibility.id,
                    BillingOrder.status == "pending",
                )
            )
        ).scalars().all()
        for order in orders:
            order.status = "expired"
            order.updated_at = now
            await log_billing_event(
                db,
                "order_expired",
                user_id=order.user_id,
                offer_id=order.offer_id,
                eligibility_id=order.eligibility_id,
                order_id=order.id,
            )
        await log_billing_event(
            db,
            "eligibility_expired",
            user_id=eligibility.user_id,
            offer_id=eligibility.offer_id,
            eligibility_id=eligibility.id,
        )


async def get_seed_offer_summary(db: AsyncSession, offer: BillingOffer) -> dict:
    free_used = (
        await db.execute(
            select(func.count()).select_from(BillingEligibility).where(
                BillingEligibility.offer_id == offer.id,
                BillingEligibility.type == FREE_ELIGIBILITY,
                BillingEligibility.status.in_(["locked", "converted"]),
            )
        )
    ).scalar() or 0
    paid_locked = (
        await db.execute(
            select(func.count()).select_from(BillingEligibility).where(
                BillingEligibility.offer_id == offer.id,
                BillingEligibility.type == PAID_ELIGIBILITY,
                BillingEligibility.status == "locked",
            )
        )
    ).scalar() or 0
    paid_paid = (
        await db.execute(
            select(func.count()).select_from(BillingEligibility).where(
                BillingEligibility.offer_id == offer.id,
                BillingEligibility.type == PAID_ELIGIBILITY,
                BillingEligibility.status == "converted",
            )
        )
    ).scalar() or 0
    paid_expired = (
        await db.execute(
            select(func.count()).select_from(BillingEligibility).where(
                BillingEligibility.offer_id == offer.id,
                BillingEligibility.type == PAID_ELIGIBILITY,
                BillingEligibility.status == "expired",
            )
        )
    ).scalar() or 0

    return {
        "free_used": int(free_used or 0),
        "paid_locked": int(paid_locked or 0),
        "paid_paid": int(paid_paid or 0),
        "paid_expired": int(paid_expired or 0),
    }


async def get_active_lifetime_entitlement(db: AsyncSession, user_id: str) -> BillingEntitlement | None:
    return (
        await db.execute(
            select(BillingEntitlement).where(
                BillingEntitlement.user_id == user_id,
                BillingEntitlement.type == ENTITLEMENT_LIFETIME,
                BillingEntitlement.status == "active",
            )
        )
    ).scalar_one_or_none()


async def get_current_eligibility(
    db: AsyncSession,
    offer_id: str,
    user_id: str,
) -> BillingEligibility | None:
    return (
        await db.execute(
            select(BillingEligibility)
            .where(
                BillingEligibility.offer_id == offer_id,
                BillingEligibility.user_id == user_id,
                BillingEligibility.status.in_(ACTIVE_ELIGIBILITY_STATUSES),
            )
            .order_by(BillingEligibility.created_at.desc())
        )
    ).scalars().first()


async def get_latest_order(
    db: AsyncSession,
    eligibility_id: str,
    statuses: set[str] | None = None,
) -> BillingOrder | None:
    stmt = (
        select(BillingOrder)
        .where(BillingOrder.eligibility_id == eligibility_id)
        .order_by(BillingOrder.created_at.desc())
    )
    if statuses:
        stmt = stmt.where(BillingOrder.status.in_(statuses))
    return (await db.execute(stmt)).scalars().first()


def _offer_status_for_payload(offer: BillingOffer, summary: dict, has_user_state: bool) -> str:
    if offer.status != "active":
        return offer.status
    free_left = max(int(offer.free_total or 0) - int(summary.get("free_used") or 0), 0)
    paid_left = max(
        int(offer.paid_total or 0)
        - int(summary.get("paid_locked") or 0)
        - int(summary.get("paid_paid") or 0),
        0,
    )
    if not has_user_state and free_left == 0 and paid_left == 0:
        return "ended"
    return offer.status


async def build_seed_offer_payload(db: AsyncSession, user: User) -> dict:
    offer = await get_or_create_seed_offer(db)
    await expire_stale_paid_reservations(db, offer)
    entitlement = await get_active_lifetime_entitlement(db, user.id)
    eligibility = await get_current_eligibility(db, offer.id, user.id)
    order = await get_latest_order(db, eligibility.id, PAYABLE_ORDER_STATUSES) if eligibility else None
    summary = await get_seed_offer_summary(db, offer)
    offer_status = _offer_status_for_payload(offer, summary, bool(eligibility or entitlement))

    return {
        "offer": serialize_offer(offer, status=offer_status),
        "summary": summary,
        "eligibility": serialize_eligibility(eligibility),
        "order": serialize_order(order),
        "current_order": serialize_order(order),
        "entitlement": serialize_entitlement(entitlement),
        "entitlements": [serialize_entitlement(entitlement)] if entitlement else [],
    }


async def grant_lifetime_entitlement(
    db: AsyncSession,
    user_id: str,
    *,
    source: str,
    offer_id: str | None = None,
    eligibility_id: str | None = None,
    order_id: str | None = None,
    notes: str | None = None,
) -> BillingEntitlement:
    now = _now()
    entitlement = (
        await db.execute(
            select(BillingEntitlement).where(
                BillingEntitlement.user_id == user_id,
                BillingEntitlement.type == ENTITLEMENT_LIFETIME,
            )
        )
    ).scalar_one_or_none()

    if entitlement:
        entitlement.status = "active"
        entitlement.source = entitlement.source or source
        entitlement.offer_id = entitlement.offer_id or offer_id
        entitlement.eligibility_id = entitlement.eligibility_id or eligibility_id
        entitlement.order_id = entitlement.order_id or order_id
        entitlement.starts_at = entitlement.starts_at or now
        entitlement.expires_at = None
        entitlement.updated_at = now
    else:
        entitlement = BillingEntitlement(
            user_id=user_id,
            offer_id=offer_id,
            eligibility_id=eligibility_id,
            order_id=order_id,
            type=ENTITLEMENT_LIFETIME,
            status="active",
            source=source,
            starts_at=now,
        )
        db.add(entitlement)

    await db.flush()

    if source == "seed_free":
        plan_code = "free_seed"
        usage_source = "seed"
    elif source == "seed_paid":
        plan_code = "seed_lifetime_9_9"
        usage_source = "payment"
    else:
        plan_code = "custom"
        usage_source = "manual"

    await upsert_user_usage_plan(
        db,
        user_id,
        {
            "plan_code": plan_code,
            "plan_name": PLAN_LABELS.get(plan_code, plan_code),
            "status": "active",
            "source": usage_source,
            "starts_at": now,
            "expires_at": None,
            "notes": notes,
        },
    )

    await log_billing_event(
        db,
        "entitlement_granted",
        user_id=user_id,
        offer_id=offer_id,
        eligibility_id=eligibility_id,
        order_id=order_id,
        entitlement_id=entitlement.id,
        payload={"source": source},
    )
    return entitlement


async def claim_seed_offer(db: AsyncSession, user: User) -> dict:
    offer = await lock_seed_offer(db)
    await expire_stale_paid_reservations(db, offer)

    if await get_active_lifetime_entitlement(db, user.id):
        return await build_seed_offer_payload(db, user)

    existing = await get_current_eligibility(db, offer.id, user.id)
    if existing:
        return await build_seed_offer_payload(db, user)

    summary = await get_seed_offer_summary(db, offer)
    now = _now()

    if offer.status == "active" and int(summary["free_used"]) < int(offer.free_total or 0):
        eligibility = BillingEligibility(
            offer_id=offer.id,
            user_id=user.id,
            type=FREE_ELIGIBILITY,
            status="converted",
            slot_no=int(summary["free_used"]) + 1,
            converted_at=now,
        )
        db.add(eligibility)
        await db.flush()
        await log_billing_event(
            db,
            "eligibility_claimed",
            user_id=user.id,
            offer_id=offer.id,
            eligibility_id=eligibility.id,
            payload={"type": FREE_ELIGIBILITY},
        )
        await grant_lifetime_entitlement(
            db,
            user.id,
            source="seed_free",
            offer_id=offer.id,
            eligibility_id=eligibility.id,
        )
        return await build_seed_offer_payload(db, user)

    paid_used = int(summary["paid_locked"]) + int(summary["paid_paid"])
    if offer.status == "active" and paid_used < int(offer.paid_total or 0):
        eligibility = BillingEligibility(
            offer_id=offer.id,
            user_id=user.id,
            type=PAID_ELIGIBILITY,
            status="locked",
            slot_no=int(offer.free_total or 0) + paid_used + 1,
            expires_at=now + timedelta(minutes=int(offer.payment_window_minutes or 30)),
        )
        db.add(eligibility)
        await db.flush()
        await log_billing_event(
            db,
            "eligibility_claimed",
            user_id=user.id,
            offer_id=offer.id,
            eligibility_id=eligibility.id,
            payload={"type": PAID_ELIGIBILITY},
        )
        return await build_seed_offer_payload(db, user)

    return await build_seed_offer_payload(db, user)


def _build_debug_payment_params(order: BillingOrder) -> dict:
    return {
        "timeStamp": str(int(_now().timestamp())),
        "nonceStr": order.order_no[-16:],
        "package": f"prepay_id=debug_{order.order_no}",
        "signType": "RSA",
        "paySign": "debug_pay_sign",
    }


def _can_return_debug_payment_params() -> bool:
    return bool(settings.DEBUG and settings.WECHAT_PAY_MOCK_IN_DEBUG)


async def create_seed_order(
    db: AsyncSession,
    user: User,
    *,
    product_type: str,
    channel: str,
) -> BillingOrder:
    if product_type != SEED_PRODUCT_TYPE:
        raise HTTPException(status_code=400, detail="不支持的商品类型")
    if channel != CHANNEL_WECHAT_MINIAPP:
        raise HTTPException(status_code=400, detail="当前仅支持微信小程序支付")

    offer = await get_or_create_seed_offer(db)
    await expire_stale_paid_reservations(db, offer)
    eligibility = await get_current_eligibility(db, offer.id, user.id)
    if not eligibility or eligibility.type != PAID_ELIGIBILITY:
        raise HTTPException(status_code=400, detail="当前账号没有可支付的种子资格")
    if eligibility.status != "locked":
        raise HTTPException(status_code=400, detail="当前种子资格无需支付或已失效")
    if eligibility.expires_at and eligibility.expires_at <= _now():
        await expire_stale_paid_reservations(db, offer)
        raise HTTPException(status_code=400, detail="支付资格已过期，请重新领取")

    existing = await get_latest_order(db, eligibility.id, PAYABLE_ORDER_STATUSES)
    if existing and (existing.status == "paid" or not existing.expires_at or existing.expires_at > _now()):
        return existing

    if not settings.WECHAT_PAY_ENABLED and not _can_return_debug_payment_params():
        raise HTTPException(status_code=503, detail="微信支付尚未配置")

    order = BillingOrder(
        order_no=_order_no(),
        user_id=user.id,
        offer_id=offer.id,
        eligibility_id=eligibility.id,
        product_type=product_type,
        channel=channel,
        status="pending",
        amount_total=int(offer.amount_cents or 990),
        currency=offer.currency or "CNY",
        expires_at=eligibility.expires_at,
    )
    db.add(order)
    await db.flush()

    if settings.WECHAT_PAY_ENABLED:
        if not (user.openid or "").strip():
            raise HTTPException(status_code=400, detail="请先使用微信登录后再支付")
        try:
            order.payment_params = await create_jsapi_payment_params(order, user)
        except WechatPayConfigError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        await log_billing_event(
            db,
            "order_created",
            user_id=user.id,
            offer_id=offer.id,
            eligibility_id=eligibility.id,
            order_id=order.id,
            payload={"channel": channel, "wechat_pay": True},
        )
        return order

    order.payment_params = _build_debug_payment_params(order)
    await log_billing_event(
        db,
        "order_created",
        user_id=user.id,
        offer_id=offer.id,
        eligibility_id=eligibility.id,
        order_id=order.id,
        payload={"channel": channel, "debug_payment": True},
    )
    return order


async def find_order_by_id_or_no(db: AsyncSession, order_id: str) -> BillingOrder | None:
    return (
        await db.execute(
            select(BillingOrder).where(or_(BillingOrder.id == order_id, BillingOrder.order_no == order_id))
        )
    ).scalar_one_or_none()


async def get_user_order(db: AsyncSession, user: User, order_id: str) -> BillingOrder:
    order = await find_order_by_id_or_no(db, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


async def mark_order_paid(
    db: AsyncSession,
    order: BillingOrder,
    *,
    transaction_id: str | None = None,
    payload: dict | None = None,
) -> BillingOrder:
    if order.status == "paid":
        return order

    if order.amount_total != int((payload or {}).get("amount_total", order.amount_total)):
        raise HTTPException(status_code=400, detail="支付金额不匹配")

    now = _now()
    order.status = "paid"
    order.transaction_id = transaction_id or order.transaction_id
    order.raw_payload = payload or order.raw_payload
    order.paid_at = now
    order.updated_at = now

    eligibility = await db.get(BillingEligibility, order.eligibility_id)
    if eligibility:
        eligibility.status = "converted"
        eligibility.converted_at = eligibility.converted_at or now
        eligibility.updated_at = now

    entitlement = await grant_lifetime_entitlement(
        db,
        order.user_id,
        source="seed_paid",
        offer_id=order.offer_id,
        eligibility_id=order.eligibility_id,
        order_id=order.id,
    )
    await log_billing_event(
        db,
        "order_paid",
        user_id=order.user_id,
        offer_id=order.offer_id,
        eligibility_id=order.eligibility_id,
        order_id=order.id,
        entitlement_id=entitlement.id,
        payload={"transaction_id": transaction_id},
    )
    return order


async def handle_wechat_payment_notify(db: AsyncSession, payload: dict) -> dict:
    order_key = payload.get("order_id") or payload.get("out_trade_no") or payload.get("order_no")
    if not order_key:
        raise HTTPException(status_code=400, detail="缺少订单号")
    order = await find_order_by_id_or_no(db, str(order_key))
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    trade_state = str(payload.get("trade_state") or payload.get("status") or "").upper()
    if trade_state not in {"SUCCESS", "PAID", "PAID_SUCCESS"}:
        await log_billing_event(
            db,
            "payment_notify_ignored",
            user_id=order.user_id,
            offer_id=order.offer_id,
            eligibility_id=order.eligibility_id,
            order_id=order.id,
            payload=payload,
        )
        return {"code": "SUCCESS", "message": "ignored"}

    await mark_order_paid(
        db,
        order,
        transaction_id=payload.get("transaction_id"),
        payload=payload,
    )
    return {"code": "SUCCESS", "message": "成功"}


async def list_entitlements_for_user(db: AsyncSession, user_id: str) -> dict:
    entitlements = (
        await db.execute(
            select(BillingEntitlement)
            .where(BillingEntitlement.user_id == user_id)
            .order_by(BillingEntitlement.created_at.desc())
        )
    ).scalars().all()
    items = [serialize_entitlement(item) for item in entitlements]
    return {
        "entitlements": items,
        "has_lifetime_access": any(item and item.get("type") == ENTITLEMENT_LIFETIME and item.get("active") for item in items),
    }


async def close_order(db: AsyncSession, order_id: str, admin_user_id: str) -> BillingOrder:
    order = await find_order_by_id_or_no(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status == "pending":
        order.status = "closed"
        order.updated_at = _now()
        await log_billing_event(
            db,
            "order_closed",
            user_id=order.user_id,
            offer_id=order.offer_id,
            eligibility_id=order.eligibility_id,
            order_id=order.id,
            payload={"admin_user_id": admin_user_id},
        )
    return order


async def release_eligibility(
    db: AsyncSession,
    eligibility_id: str,
    admin_user_id: str,
) -> BillingEligibility:
    eligibility = await db.get(BillingEligibility, eligibility_id)
    if not eligibility:
        raise HTTPException(status_code=404, detail="资格不存在")
    if eligibility.status == "locked":
        eligibility.status = "expired"
        eligibility.updated_at = _now()
        orders = (
            await db.execute(
                select(BillingOrder).where(
                    BillingOrder.eligibility_id == eligibility.id,
                    BillingOrder.status == "pending",
                )
            )
        ).scalars().all()
        for order in orders:
            order.status = "expired"
            order.updated_at = _now()
        await log_billing_event(
            db,
            "eligibility_released",
            user_id=eligibility.user_id,
            offer_id=eligibility.offer_id,
            eligibility_id=eligibility.id,
            payload={"admin_user_id": admin_user_id},
        )
    return eligibility


async def admin_seed_summary(db: AsyncSession) -> dict:
    offer = await get_or_create_seed_offer(db)
    await expire_stale_paid_reservations(db, offer)
    summary = await get_seed_offer_summary(db, offer)
    return {"offer": serialize_offer(offer), "summary": summary}


async def list_admin_eligibilities(
    db: AsyncSession,
    *,
    status: str | None,
    page: int,
    page_size: int,
) -> dict:
    offer = await get_or_create_seed_offer(db)
    conditions = [BillingEligibility.offer_id == offer.id]
    if status:
        conditions.append(BillingEligibility.status == status)

    total = (
        await db.execute(select(func.count()).select_from(BillingEligibility).where(and_(*conditions)))
    ).scalar() or 0
    rows = (
        await db.execute(
            select(BillingEligibility, User)
            .join(User, BillingEligibility.user_id == User.id)
            .where(and_(*conditions))
            .order_by(BillingEligibility.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).all()
    items = []
    for eligibility, user in rows:
        data = serialize_eligibility(eligibility) or {}
        data.update({"username": user.username, "nickname": user.nickname})
        items.append(data)
    return {"total": int(total or 0), "page": page, "page_size": page_size, "items": items}


async def list_admin_orders(
    db: AsyncSession,
    *,
    status: str | None,
    page: int,
    page_size: int,
) -> dict:
    conditions = []
    if status:
        conditions.append(BillingOrder.status == status)
    where_clause = and_(*conditions) if conditions else None
    count_stmt = select(func.count()).select_from(BillingOrder)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(BillingOrder, User)
        .join(User, BillingOrder.user_id == User.id)
        .order_by(BillingOrder.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if where_clause is not None:
        stmt = stmt.where(where_clause)
    rows = (await db.execute(stmt)).all()
    items = []
    for order, user in rows:
        data = serialize_order(order) or {}
        data.update({"username": user.username, "nickname": user.nickname})
        items.append(data)
    return {"total": int(total or 0), "page": page, "page_size": page_size, "items": items}


async def list_admin_entitlements(
    db: AsyncSession,
    *,
    status: str | None,
    page: int,
    page_size: int,
) -> dict:
    conditions = []
    if status:
        conditions.append(BillingEntitlement.status == status)
    where_clause = and_(*conditions) if conditions else None
    count_stmt = select(func.count()).select_from(BillingEntitlement)
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(BillingEntitlement, User)
        .join(User, BillingEntitlement.user_id == User.id)
        .order_by(BillingEntitlement.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if where_clause is not None:
        stmt = stmt.where(where_clause)
    rows = (await db.execute(stmt)).all()
    items = []
    for entitlement, user in rows:
        data = serialize_entitlement(entitlement) or {}
        data.update({"username": user.username, "nickname": user.nickname})
        items.append(data)
    return {"total": int(total or 0), "page": page, "page_size": page_size, "items": items}
