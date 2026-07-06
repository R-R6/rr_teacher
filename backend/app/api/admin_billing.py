"""Admin billing APIs for seed offer operations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.database import get_db
from app.models import User
from app.schemas import AdminBillingGrantEntitlementReq, ApiResp
from app.services.billing_service import (
    admin_seed_summary,
    close_order,
    grant_lifetime_entitlement,
    list_admin_eligibilities,
    list_admin_entitlements,
    list_admin_orders,
    release_eligibility,
    serialize_eligibility,
    serialize_entitlement,
    serialize_order,
)


router = APIRouter()


@router.get("/seed-summary", response_model=ApiResp)
async def get_seed_summary(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await admin_seed_summary(db))


@router.get("/eligibilities", response_model=ApiResp)
async def get_eligibilities(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await list_admin_eligibilities(db, status=status, page=page, page_size=page_size))


@router.get("/orders", response_model=ApiResp)
async def get_orders(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await list_admin_orders(db, status=status, page=page, page_size=page_size))


@router.get("/entitlements", response_model=ApiResp)
async def get_entitlements(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return ApiResp(data=await list_admin_entitlements(db, status=status, page=page, page_size=page_size))


@router.post("/orders/{order_id}/close", response_model=ApiResp)
async def close_billing_order(
    order_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    order = await close_order(db, order_id, current_user.id)
    return ApiResp(message="订单已关闭", data=serialize_order(order))


@router.post("/eligibilities/{eligibility_id}/release", response_model=ApiResp)
async def release_billing_eligibility(
    eligibility_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    eligibility = await release_eligibility(db, eligibility_id, current_user.id)
    return ApiResp(message="资格已释放", data=serialize_eligibility(eligibility))


@router.post("/entitlements/grant", response_model=ApiResp)
async def grant_entitlement(
    req: AdminBillingGrantEntitlementReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    entitlement = await grant_lifetime_entitlement(
        db,
        req.user_id,
        source=req.source,
        notes=req.notes,
    )
    return ApiResp(message="权益已发放", data=serialize_entitlement(entitlement))
