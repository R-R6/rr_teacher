import unittest
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.models import Base, User
from app.services.billing_service import (
    CHANNEL_WECHAT_MINIAPP,
    SEED_PRODUCT_TYPE,
    claim_seed_offer,
    create_seed_order,
    get_active_lifetime_entitlement,
    handle_wechat_payment_notify,
)
from app.services.usage_plan_service import get_user_usage_plan


class BillingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        asyncio.get_running_loop().set_debug(False)
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def _create_user(self, db, username: str) -> User:
        user = User(
            username=username,
            hashed_password="test",
            role="teacher",
            nickname=username,
            is_active=True,
            created_at=datetime.now(),
        )
        db.add(user)
        await db.flush()
        return user

    async def test_free_seed_claim_grants_entitlement_and_usage_plan(self):
        async with self.Session() as db:
            user = await self._create_user(db, "teacher_free")

            payload = await claim_seed_offer(db, user)

            self.assertEqual(payload["eligibility"]["type"], "free_seed")
            self.assertEqual(payload["eligibility"]["status"], "converted")
            self.assertEqual(payload["entitlement"]["type"], "lifetime_access")
            self.assertTrue(payload["entitlement"]["active"])

            profile = await get_user_usage_plan(db, user.id)
            self.assertIsNotNone(profile)
            self.assertEqual(profile.plan_code, "free_seed")
            self.assertEqual(profile.source, "seed")

    async def test_paid_seed_order_notify_grants_entitlement_and_usage_plan(self):
        async with self.Session() as db:
            users = [await self._create_user(db, f"teacher_{index}") for index in range(11)]
            for user in users[:10]:
                await claim_seed_offer(db, user)

            paid_user = users[10]
            payload = await claim_seed_offer(db, paid_user)
            self.assertEqual(payload["eligibility"]["type"], "paid_seed_9_9")
            self.assertEqual(payload["eligibility"]["status"], "locked")

            order = await create_seed_order(
                db,
                paid_user,
                product_type=SEED_PRODUCT_TYPE,
                channel=CHANNEL_WECHAT_MINIAPP,
            )
            self.assertEqual(order.status, "pending")
            self.assertIn("paySign", order.payment_params)

            result = await handle_wechat_payment_notify(
                db,
                {
                    "order_no": order.order_no,
                    "trade_state": "SUCCESS",
                    "transaction_id": "wx-test-001",
                    "amount_total": order.amount_total,
                },
            )
            self.assertEqual(result["code"], "SUCCESS")
            self.assertEqual(order.status, "paid")

            entitlement = await get_active_lifetime_entitlement(db, paid_user.id)
            self.assertIsNotNone(entitlement)
            self.assertEqual(entitlement.source, "seed_paid")

            profile = await get_user_usage_plan(db, paid_user.id)
            self.assertIsNotNone(profile)
            self.assertEqual(profile.plan_code, "seed_lifetime_9_9")
            self.assertEqual(profile.source, "payment")

    async def test_create_seed_order_requires_openid_when_wechat_pay_enabled(self):
        async with self.Session() as db:
            users = [await self._create_user(db, f"openid_user_{index}") for index in range(11)]
            for user in users[:10]:
                await claim_seed_offer(db, user)

            paid_user = users[10]
            await claim_seed_offer(db, paid_user)

            with patch.object(settings, "WECHAT_PAY_ENABLED", True), patch.object(
                settings, "WECHAT_PAY_MOCK_IN_DEBUG", False
            ), patch.object(settings, "DEBUG", False):
                with self.assertRaises(HTTPException) as ctx:
                    await create_seed_order(
                        db,
                        paid_user,
                        product_type=SEED_PRODUCT_TYPE,
                        channel=CHANNEL_WECHAT_MINIAPP,
                    )
                self.assertEqual(ctx.exception.status_code, 400)
                self.assertIn("微信登录", ctx.exception.detail)

    async def test_create_seed_order_uses_wechat_pay_adapter_when_enabled(self):
        async with self.Session() as db:
            users = [await self._create_user(db, f"pay_user_{index}") for index in range(11)]
            for user in users[:10]:
                await claim_seed_offer(db, user)

            paid_user = users[10]
            paid_user.openid = "o-test-openid"
            await db.flush()
            await claim_seed_offer(db, paid_user)

            mock_params = {
                "timeStamp": "1700000000",
                "nonceStr": "nonce-test",
                "package": "prepay_id=wx_test",
                "signType": "RSA",
                "paySign": "signed",
            }

            with patch.object(settings, "WECHAT_PAY_ENABLED", True), patch.object(
                settings, "WECHAT_PAY_MOCK_IN_DEBUG", False
            ), patch(
                "app.services.billing_service.create_jsapi_payment_params",
                new=AsyncMock(return_value=mock_params),
            ):
                order = await create_seed_order(
                    db,
                    paid_user,
                    product_type=SEED_PRODUCT_TYPE,
                    channel=CHANNEL_WECHAT_MINIAPP,
                )

            self.assertEqual(order.status, "pending")
            self.assertEqual(order.payment_params, mock_params)


if __name__ == "__main__":
    unittest.main()
