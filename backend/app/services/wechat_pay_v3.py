"""WeChat Pay API v3 helpers for mini program JSAPI payments."""

from __future__ import annotations

import base64
import json
import secrets
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings
from app.models import BillingOrder, User


JSAPI_TRANSACTIONS_PATH = "/v3/pay/transactions/jsapi"
PAYMENT_DESCRIPTION = "种子计划 · 终身权益"


class WechatPayConfigError(RuntimeError):
    pass


class WechatPaySignatureError(RuntimeError):
    pass


def _require(value: str, name: str) -> str:
    if not (value or "").strip():
        raise WechatPayConfigError(f"{name} is required when WECHAT_PAY_ENABLED=true")
    return value.strip()


def _nonce() -> str:
    return secrets.token_urlsafe(24)[:32]


def _load_private_key():
    raw_private_key = (settings.WECHAT_PAY_PRIVATE_KEY or "").strip()
    private_key_path = (settings.WECHAT_PAY_PRIVATE_KEY_PATH or "").strip()
    if raw_private_key:
        key_data = raw_private_key.replace("\\n", "\n").encode("utf-8")
    elif private_key_path:
        key_data = Path(private_key_path).read_bytes()
    else:
        raise WechatPayConfigError("WECHAT_PAY_PRIVATE_KEY_PATH or WECHAT_PAY_PRIVATE_KEY is required")

    return serialization.load_pem_private_key(key_data, password=None)


def _sign(message: str) -> str:
    signature = _load_private_key().sign(
        message.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def _request_authorization(method: str, path: str, body: str, timestamp: str, nonce: str) -> str:
    mch_id = _require(settings.WECHAT_PAY_MCH_ID, "WECHAT_PAY_MCH_ID")
    serial_no = _require(settings.WECHAT_PAY_MCH_SERIAL_NO, "WECHAT_PAY_MCH_SERIAL_NO")
    message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}\n"
    signature = _sign(message)
    return (
        'WECHATPAY2-SHA256-RSA2048 '
        f'mchid="{mch_id}",nonce_str="{nonce}",signature="{signature}",'
        f'timestamp="{timestamp}",serial_no="{serial_no}"'
    )


def build_request_payment_params(prepay_id: str) -> dict:
    appid = _require(settings.WECHAT_APPID, "WECHAT_APPID")
    timestamp = str(int(time.time()))
    nonce = _nonce()
    package = f"prepay_id={prepay_id}"
    message = f"{appid}\n{timestamp}\n{nonce}\n{package}\n"
    return {
        "timeStamp": timestamp,
        "nonceStr": nonce,
        "package": package,
        "signType": "RSA",
        "paySign": _sign(message),
    }


async def create_jsapi_payment_params(order: BillingOrder, user: User) -> dict:
    if not (user.openid or "").strip():
        raise WechatPayConfigError("User openid is required for WeChat mini program payment")

    api_base = (settings.WECHAT_PAY_API_BASE or "https://api.mch.weixin.qq.com").rstrip("/")
    notify_url = _require(settings.WECHAT_PAY_NOTIFY_URL, "WECHAT_PAY_NOTIFY_URL")
    body = {
        "appid": _require(settings.WECHAT_APPID, "WECHAT_APPID"),
        "mchid": _require(settings.WECHAT_PAY_MCH_ID, "WECHAT_PAY_MCH_ID"),
        "description": PAYMENT_DESCRIPTION,
        "out_trade_no": order.order_no,
        "notify_url": notify_url,
        "amount": {
            "total": int(order.amount_total),
            "currency": order.currency or "CNY",
        },
        "payer": {
            "openid": user.openid,
        },
    }
    body_text = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    timestamp = str(int(time.time()))
    nonce = _nonce()
    headers = {
        "Authorization": _request_authorization("POST", JSAPI_TRANSACTIONS_PATH, body_text, timestamp, nonce),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "rr-teacher-backend",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(f"{api_base}{JSAPI_TRANSACTIONS_PATH}", content=body_text.encode("utf-8"), headers=headers)
    response.raise_for_status()
    data = response.json()
    prepay_id = data.get("prepay_id")
    if not prepay_id:
        raise RuntimeError("WeChat Pay response missing prepay_id")
    return build_request_payment_params(str(prepay_id))


def _platform_public_key():
    cert_path = _require(settings.WECHAT_PAY_PLATFORM_CERT_PATH, "WECHAT_PAY_PLATFORM_CERT_PATH")
    certificate = x509.load_pem_x509_certificate(Path(cert_path).read_bytes())
    return certificate.public_key()


def verify_notification_signature(raw_body: bytes, headers: dict) -> None:
    timestamp = headers.get("wechatpay-timestamp") or headers.get("Wechatpay-Timestamp")
    nonce = headers.get("wechatpay-nonce") or headers.get("Wechatpay-Nonce")
    signature = headers.get("wechatpay-signature") or headers.get("Wechatpay-Signature")
    if not timestamp or not nonce or not signature:
        raise WechatPaySignatureError("Missing WeChat Pay notification signature headers")

    message = f"{timestamp}\n{nonce}\n{raw_body.decode('utf-8')}\n".encode("utf-8")
    try:
        _platform_public_key().verify(
            base64.b64decode(signature),
            message,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except (InvalidSignature, ValueError) as exc:
        raise WechatPaySignatureError("Invalid WeChat Pay notification signature") from exc


def decrypt_notification_resource(resource: dict) -> dict:
    api_v3_key = _require(settings.WECHAT_PAY_API_V3_KEY, "WECHAT_PAY_API_V3_KEY").encode("utf-8")
    if len(api_v3_key) != 32:
        raise WechatPayConfigError("WECHAT_PAY_API_V3_KEY must be 32 bytes")

    nonce = str(resource.get("nonce") or "").encode("utf-8")
    ciphertext = base64.b64decode(resource.get("ciphertext") or "")
    associated_data = str(resource.get("associated_data") or "").encode("utf-8")
    plaintext = AESGCM(api_v3_key).decrypt(nonce, ciphertext, associated_data)
    return json.loads(plaintext.decode("utf-8"))


def parse_notification(raw_body: bytes, headers: dict) -> dict:
    payload = json.loads(raw_body.decode("utf-8"))
    if settings.DEBUG and "resource" not in payload:
        return payload

    verify_notification_signature(raw_body, headers)
    resource = payload.get("resource")
    if not isinstance(resource, dict):
        raise WechatPaySignatureError("Missing WeChat Pay encrypted resource")
    transaction = decrypt_notification_resource(resource)
    if transaction.get("appid") != settings.WECHAT_APPID:
        raise WechatPaySignatureError("WeChat Pay notification appid mismatch")
    if transaction.get("mchid") != settings.WECHAT_PAY_MCH_ID:
        raise WechatPaySignatureError("WeChat Pay notification mchid mismatch")
    return transaction


def normalize_transaction_payload(transaction: dict) -> dict:
    amount = transaction.get("amount") or {}
    order_key = transaction.get("out_trade_no") or transaction.get("order_no") or transaction.get("order_id")
    return {
        **transaction,
        "out_trade_no": order_key,
        "order_no": order_key,
        "order_id": order_key,
        "trade_state": transaction.get("trade_state") or transaction.get("status"),
        "transaction_id": transaction.get("transaction_id"),
        "amount_total": amount.get("total", transaction.get("amount_total")),
    }


def notify_url_path() -> str:
    notify_url = _require(settings.WECHAT_PAY_NOTIFY_URL, "WECHAT_PAY_NOTIFY_URL")
    parsed = urlparse(notify_url)
    return parsed.path or "/api/billing/payments/wechat/notify"
