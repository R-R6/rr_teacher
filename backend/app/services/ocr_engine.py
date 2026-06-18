"""
OCR engine adapters.

Supported engines:
- tesseract: local Tesseract OCR, low cost and cloud-friendly
- pix2text_online: official Pix2Text async API
- pix2text_local: local Pix2Text inference for development only
"""

import asyncio
import logging
import os
from typing import Optional

import httpx
from PIL import Image, ImageEnhance, ImageFilter

from app.config import settings
from app.services.doubao_ocr import doubao_vision_recognize

logger = logging.getLogger(__name__)


async def recognize_image(image_path: str, engine: str = "tesseract", **options) -> dict:
    """Unified OCR entry point."""
    engine = (engine or "tesseract").lower()
    if engine == "tesseract":
        return await _tesseract_recognize(image_path, **options)
    if engine == "pix2text_online":
        return await _pix2text_online_recognize(image_path, **options)
    if engine == "pix2text_local":
        return await _pix2text_local_recognize(image_path, **options)
    if engine == "doubao_vision":
        return await doubao_vision_recognize(image_path, **options)
    return {
        "text": "",
        "latex": "",
        "confidence": 0.0,
        "engine": f"unknown:{engine}",
        "images": [],
        "error": f"Unsupported OCR engine: {engine}",
    }


_TESSERACT_PATHS = [
    r"D:\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/opt/homebrew/bin/tesseract",
    "/usr/local/Cellar/tesseract/*/bin/tesseract",
]


def _detect_tesseract() -> Optional[str]:
    try:
        import pytesseract  # noqa: F401
    except ImportError:
        return None

    if settings.TESSERACT_PATH and os.path.exists(settings.TESSERACT_PATH):
        return settings.TESSERACT_PATH

    env_path = os.environ.get("TESSERACT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    from shutil import which

    system_path = which("tesseract")
    if system_path:
        return system_path

    for candidate in _TESSERACT_PATHS:
        if "*" in candidate:
            import glob

            for matched in glob.glob(candidate):
                if os.path.exists(matched):
                    return matched
        elif os.path.exists(candidate):
            return candidate
    return None


def _tesseract_preprocess(image_path: str) -> Image.Image:
    image = Image.open(image_path)
    if image.mode != "L":
        image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = image.filter(ImageFilter.SHARPEN)
    return image


async def _tesseract_recognize(image_path: str, lang: str = "chi_sim+eng", **options) -> dict:
    binary = _detect_tesseract()
    if not binary:
        logger.warning("Tesseract not found")
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "tesseract-missing",
            "images": [],
            "error": "Tesseract is not installed",
        }

    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = binary

    if not os.environ.get("TESSDATA_PREFIX") and not settings.TESSDATA_PREFIX:
        candidate = os.path.join(os.path.dirname(binary), "tessdata")
        if os.path.isdir(candidate):
            os.environ["TESSDATA_PREFIX"] = candidate

    try:
        image = _tesseract_preprocess(image_path)
        try:
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                output_type=pytesseract.Output.DICT,
            )
            text = pytesseract.image_to_string(image, lang=lang).strip()
            confs = [int(value) for value in data.get("conf", []) if value not in ("-1", -1)]
            avg_confidence = (sum(confs) / len(confs) / 100.0) if confs else 0.0
        except Exception:
            text = pytesseract.image_to_string(image, lang=lang).strip()
            avg_confidence = 0.0

        return {
            "text": text,
            "latex": text,
            "confidence": round(avg_confidence, 3),
            "engine": "tesseract",
            "images": [],
        }
    except Exception as exc:
        logger.error("Tesseract recognition failed: %s", exc)
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "tesseract-error",
            "images": [],
            "error": str(exc),
        }


DEFAULT_PIX2TEXT_URL = "https://api.breezedeus.com/api/pix2text"


async def _pix2text_online_recognize(image_path: str, **options) -> dict:
    """
    Call the official Pix2Text async API:
    1. POST /api/pix2text
    2. poll GET /api/result/{task_id}
    """
    token = settings.PIX2TEXT_API_TOKEN
    url = settings.PIX2TEXT_API_URL or DEFAULT_PIX2TEXT_URL
    language = options.get("language") or "Simplified Chinese"
    file_type = options.get("file_type") or "text_formula"
    server_type = options.get("server_type") or "pro"
    poll_interval = float(options.get("poll_interval") or 1.5)
    max_polls = int(options.get("max_polls") or 40)

    if not token:
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "pix2text_online",
            "images": [],
            "error": "Pix2Text API token is not configured",
        }

    try:
        with open(image_path, "rb") as file_obj:
            file_bytes = file_obj.read()

        ext = (os.path.splitext(image_path)[1] or ".jpg").lower()
        mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }.get(ext, "image/jpeg")
        file_name = os.path.basename(image_path) or "image.jpg"

        async with httpx.AsyncClient(timeout=60.0) as client:
            submit_resp = await client.post(
                url,
                headers={"X-API-Key": token},
                files={"image": (file_name, file_bytes, mime)},
                data={
                    "language": language,
                    "file_type": file_type,
                    "server_type": server_type,
                },
            )

            if submit_resp.status_code != 200:
                return {
                    "text": "",
                    "latex": "",
                    "confidence": 0.0,
                    "engine": "pix2text_online",
                    "images": [],
                    "error": f"Pix2Text submit {submit_resp.status_code}: {submit_resp.text[:300]}",
                }

            submit_payload = submit_resp.json()
            task_id = submit_payload.get("task_id")
            if not task_id:
                return {
                    "text": "",
                    "latex": "",
                    "confidence": 0.0,
                    "engine": "pix2text_online",
                    "images": [],
                    "error": f"Pix2Text submit missing task_id: {submit_payload}",
                }

            result_url = f"{url.rsplit('/', 1)[0]}/result/{task_id}"
            result_payload = None
            for _ in range(max_polls):
                result_resp = await client.get(
                    result_url,
                    headers={"X-API-Key": token},
                )
                if result_resp.status_code != 200:
                    return {
                        "text": "",
                        "latex": "",
                        "confidence": 0.0,
                        "engine": "pix2text_online",
                        "images": [],
                        "error": f"Pix2Text result {result_resp.status_code}: {result_resp.text[:300]}",
                    }

                result_payload = result_resp.json()
                status = str(result_payload.get("status", "")).upper()
                if status == "FINISHED":
                    break
                if status in {"FAILED", "ERROR"}:
                    return {
                        "text": "",
                        "latex": "",
                        "confidence": 0.0,
                        "engine": "pix2text_online",
                        "images": [],
                        "error": f"Pix2Text task failed: {result_payload}",
                        "raw": {"submit": submit_payload, "result": result_payload},
                    }
                await asyncio.sleep(poll_interval)

        if not result_payload or str(result_payload.get("status", "")).upper() != "FINISHED":
            return {
                "text": "",
                "latex": "",
                "confidence": 0.0,
                "engine": "pix2text_online",
                "images": [],
                "error": "Pix2Text result polling timed out",
                "raw": {"submit": submit_payload, "result": result_payload},
            }

        result_text = result_payload.get("results") or result_payload.get("text") or ""
        return {
            "text": result_text,
            "latex": result_text,
            "confidence": 0.95,
            "engine": "pix2text_online",
            "images": [],
            "raw": {"submit": submit_payload, "result": result_payload},
        }
    except httpx.TimeoutException:
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "pix2text_online",
            "images": [],
            "error": "Pix2Text online API timeout",
        }
    except Exception as exc:
        logger.error("Pix2Text online recognize failed: %s", exc)
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "pix2text_online",
            "images": [],
            "error": f"Pix2Text call failed: {exc}",
        }


_pix2text_local = None
_pix2text_load_attempted = False


def _load_pix2text_local():
    global _pix2text_local, _pix2text_load_attempted
    if _pix2text_load_attempted:
        return _pix2text_local

    _pix2text_load_attempted = True
    try:
        from pix2text import Pix2Text

        _pix2text_local = Pix2Text.from_config()
        logger.info("Pix2Text local model loaded")
    except Exception as exc:
        logger.warning("Pix2Text local model load failed: %s", exc)
        _pix2text_local = None
    return _pix2text_local


async def _pix2text_local_recognize(image_path: str, **options) -> dict:
    p2t = _load_pix2text_local()
    if p2t is None:
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "pix2text_local",
            "images": [],
            "error": "Pix2Text local model is not installed",
        }

    try:
        result = await asyncio.to_thread(
            p2t.recognize,
            image_path,
            file_type="page",
            resized_shape=768,
        )
        text = result if isinstance(result, str) else getattr(result, "text", "") or str(result)
        return {
            "text": text,
            "latex": text,
            "confidence": 0.95,
            "engine": "pix2text_local",
            "images": [],
        }
    except Exception as exc:
        logger.error("Pix2Text local recognize failed: %s", exc)
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "pix2text_local",
            "images": [],
            "error": str(exc),
        }
