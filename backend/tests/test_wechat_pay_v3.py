import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.services import wechat_pay_v3


class WechatPayV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.private_key_pem = cls.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def test_build_request_payment_params(self):
        def fake_require(value, name):
            if name == "WECHAT_APPID":
                return "wx_test_appid"
            return value

        with patch.object(wechat_pay_v3, "_require", side_effect=fake_require), patch.object(
            wechat_pay_v3, "_load_private_key", return_value=self.private_key
        ):
            params = wechat_pay_v3.build_request_payment_params("wx2026070612345678")

        self.assertTrue(params["timeStamp"].isdigit())
        self.assertTrue(params["nonceStr"])
        self.assertEqual(params["package"], "prepay_id=wx2026070612345678")
        self.assertEqual(params["signType"], "RSA")
        self.assertTrue(params["paySign"])

    def test_normalize_transaction_payload_maps_order_and_amount(self):
        payload = wechat_pay_v3.normalize_transaction_payload(
            {
                "out_trade_no": "B20260706001",
                "trade_state": "SUCCESS",
                "transaction_id": "4200001234",
                "amount": {"total": 990, "currency": "CNY"},
            }
        )

        self.assertEqual(payload["order_no"], "B20260706001")
        self.assertEqual(payload["order_id"], "B20260706001")
        self.assertEqual(payload["amount_total"], 990)
        self.assertEqual(payload["trade_state"], "SUCCESS")

    def test_parse_notification_allows_debug_mock_payload(self):
        raw_body = b'{"order_no":"B001","trade_state":"SUCCESS","amount_total":990}'
        with patch.object(settings, "DEBUG", True):
            payload = wechat_pay_v3.parse_notification(raw_body, {})

        self.assertEqual(payload["order_no"], "B001")
        self.assertEqual(payload["trade_state"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
