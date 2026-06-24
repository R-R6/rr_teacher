"""
Tencent COS upload helpers.
Falls back to local filesystem storage when COS is not configured.
"""

import logging
import os
import shutil
from urllib.parse import unquote, urlparse

from app.config import settings

logger = logging.getLogger(__name__)

LOCAL_STORAGE_DIR = "./uploads"
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

try:
    from qcloud_cos import CosConfig, CosS3Client

    HAS_COS_SDK = True
except ImportError:
    HAS_COS_SDK = False
    logger.info("qcloud_cos SDK not installed, using local file storage")


def _cos_enabled() -> bool:
    return bool(settings.COS_SECRET_ID and settings.COS_BUCKET and HAS_COS_SDK)


def _get_cos_client():
    if not _cos_enabled():
        return None
    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    return CosS3Client(config)


def _build_public_cos_url(cos_key: str) -> str:
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"


def _extract_cos_key(url_or_key: str) -> str:
    if not url_or_key:
        return ""

    if url_or_key.startswith("/uploads/"):
        return url_or_key

    if url_or_key.startswith("http://") or url_or_key.startswith("https://"):
        parsed = urlparse(url_or_key)
        return unquote(parsed.path.lstrip("/"))

    return url_or_key.lstrip("/")


async def upload_to_cos(local_path: str, cos_key: str) -> str:
    """
    Upload a file to COS.
    In local mode, copy it into ./uploads and return the local URL.
    """
    if not _cos_enabled():
        dest_path = os.path.join(LOCAL_STORAGE_DIR, os.path.basename(cos_key))
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(local_path, dest_path)
        logger.info("Saved file to local storage: %s", dest_path)
        return f"/uploads/{os.path.basename(cos_key)}"

    client = _get_cos_client()
    with open(local_path, "rb") as file_obj:
        client.put_object(
            Bucket=settings.COS_BUCKET,
            Body=file_obj,
            Key=cos_key,
            EnableMD5=False,
        )
    return _build_public_cos_url(cos_key)


def get_cos_url(url_or_key: str, expires: int = 3600) -> str:
    """
    Convert a stored COS URL/key into a client-usable URL.
    For private COS buckets this returns a signed temporary URL.
    """
    key = _extract_cos_key(url_or_key)
    if not key:
        return ""

    if key.startswith("/uploads/"):
        return key

    if not _cos_enabled():
        return f"/uploads/{os.path.basename(key)}"

    client = _get_cos_client()
    try:
        return client.get_presigned_url(
            Method="GET",
            Bucket=settings.COS_BUCKET,
            Key=key,
            Expired=expires,
        )
    except Exception as exc:
        logger.warning("Failed to sign COS URL for %s: %s", key, exc)
        return _build_public_cos_url(key)


def read_storage_file(url_or_key: str) -> tuple[bytes, str]:
    """
    Read a stored file from COS or local fallback storage.
    Returns file bytes and a best-effort filename.
    """
    key = _extract_cos_key(url_or_key)
    if not key:
        raise FileNotFoundError("empty storage key")

    filename = os.path.basename(key)
    if key.startswith("/uploads/") or not _cos_enabled():
        local_path = os.path.join(LOCAL_STORAGE_DIR, filename)
        if not os.path.exists(local_path):
            raise FileNotFoundError(local_path)
        with open(local_path, "rb") as file_obj:
            return file_obj.read(), filename

    client = _get_cos_client()
    response = client.get_object(
        Bucket=settings.COS_BUCKET,
        Key=key,
    )
    stream = response["Body"].get_raw_stream()
    return stream.read(), filename


async def delete_from_cos(cos_key: str) -> bool:
    if not _cos_enabled():
        local_path = os.path.join(LOCAL_STORAGE_DIR, os.path.basename(cos_key))
        if os.path.exists(local_path):
            os.remove(local_path)
        return True

    client = _get_cos_client()
    client.delete_object(
        Bucket=settings.COS_BUCKET,
        Key=cos_key,
    )
    return True
