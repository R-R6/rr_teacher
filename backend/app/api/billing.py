"""User-facing billing APIs."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_teacher
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import ApiResp, BillingOrderCreateReq
from app.services.billing_service import (
    build_seed_offer_payload,
    claim_seed_offer,
    create_seed_order,
    get_user_order,
    handle_wechat_payment_notify,
    list_entitlements_for_user,
    serialize_order,
)
from app.services.wechat_pay_v3 import (
    WechatPaySignatureError,
    normalize_transaction_payload,
    parse_notification,
)


router = APIRouter()


@router.get("/seed-offer", response_model=ApiResp)
async def get_seed_offer(
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await build_seed_offer_payload(db, current_user))


@router.post("/seed-offer/claim", response_model=ApiResp)
async def claim_seed_offer_api(
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await claim_seed_offer(db, current_user))


@router.post("/orders", response_model=ApiResp)
async def create_order(
    req: BillingOrderCreateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    order = await create_seed_order(
        db,
        current_user,
        product_type=req.product_type,
        channel=req.channel,
    )
    return ApiResp(data=serialize_order(order))


@router.get("/orders/{order_id}", response_model=ApiResp)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    order = await get_user_order(db, current_user, order_id)
    return ApiResp(data=serialize_order(order))


@router.post("/payments/wechat/notify")
async def wechat_payment_notify(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    raw_body = await request.body()
    if not raw_body:
        raise HTTPException(status_code=400, detail="缺少回调内容")

    headers = {key.lower(): value for key, value in request.headers.items()}
    try:
        raw_payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="回调内容不是合法 JSON") from exc

    if settings.DEBUG and "resource" not in raw_payload:
        token = headers.get("x-wechat-pay-token", "")
        if settings.WECHAT_PAY_NOTIFY_TOKEN and token != settings.WECHAT_PAY_NOTIFY_TOKEN:
            raise HTTPException(status_code=403, detail="微信支付回调未授权")
        payload = raw_payload
    else:
        try:
            transaction = parse_notification(raw_body, headers)
            payload = normalize_transaction_payload(transaction)
        except WechatPaySignatureError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return await handle_wechat_payment_notify(db, payload)


@router.get("/me/entitlements", response_model=ApiResp)
async def get_my_entitlements(
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await list_entitlements_for_user(db, current_user.id))
