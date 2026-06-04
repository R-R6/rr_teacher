"""
OCR 识别引擎服务
基于 Pix2Text (P2T) 实现中文化学混排识别
"""
import json
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def recognize_image(image_path: str) -> dict:
    """
    识别图片中的化学题目

    参数:
        image_path: 本地图片路径

    返回:
        {
            "latex": "$H_2SO_4$ + $NaOH$ ⟶ $Na_2SO_4$ + $H_2O$",
            "text": "H₂SO₄ + NaOH → Na₂SO₄ + H₂O",
            "raw_json": "{...}",
            "confidence": 0.92,
            "engine": "pix2text"
        }
    """
    # 优先调用 Pix2Text 微服务
    try:
        return await _recognize_via_p2t_service(image_path)
    except Exception as e:
        logger.warning(f"Pix2Text 服务调用失败: {e}，降级到本地P2T库")
        return await _recognize_via_p2t_local(image_path)


async def _recognize_via_p2t_service(image_path: str) -> dict:
    """通过 Pix2Text HTTP 微服务识别"""
    async with httpx.AsyncClient(timeout=settings.OCR_TIMEOUT) as client:
        with open(image_path, "rb") as f:
            files = {"file": ("image.jpg", f, "image/jpeg")}
            resp = await client.post(
                f"{settings.OCR_SERVICE_URL}/recognize",
                files=files,
            )
            resp.raise_for_status()
            data = resp.json()

    return {
        "latex": data.get("latex", ""),
        "text": data.get("text", ""),
        "raw_json": json.dumps(data, ensure_ascii=False),
        "confidence": data.get("confidence", 0.0),
        "engine": "pix2text",
    }


async def _recognize_via_p2t_local(image_path: str) -> dict:
    """使用本地 Pix2Text 库识别（降级方案）"""
    try:
        from pix2text import Pix2Text
    except ImportError:
        raise ImportError(
            "Pix2Text 未安装，请执行: pip install pix2text>=1.1\n"
            "或部署OCR微服务: docker compose up ocr-service"
        )

    p2t = Pix2Text()
    result = p2t.recognize(image_path, file_type="page")

    latex_parts = []
    text_parts = []
    for item in result:
        if item.get("type") == "text":
            text_parts.append(item.get("text", ""))
            latex_parts.append(item.get("text", ""))
        elif item.get("type") == "isolated":
            latex = item.get("text", "")
            latex_parts.append(f"${latex}$")
            text_parts.append(latex)

    latex_result = "\n\n".join(latex_parts)
    text_result = "\n\n".join(text_parts)

    return {
        "latex": latex_result,
        "text": text_result,
        "raw_json": json.dumps(result, ensure_ascii=False, default=str),
        "confidence": 0.85,  # P2T 本地库不提供置信度，给默认值
        "engine": "pix2text",
    }


async def preprocess_image(image_path: str) -> str:
    """
    图片预处理：增强对比度、去噪、自动裁剪
    返回处理后的图片路径
    """
    from PIL import Image, ImageEnhance, ImageFilter

    img = Image.open(image_path)

    # 转灰度
    img = img.convert("L")

    # 增强对比度（利于公式识别）
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # 锐化
    img = img.filter(ImageFilter.SHARPEN)

    # 保存
    processed_path = image_path.replace(".", "_processed.")
    img.save(processed_path, quality=95)

    return processed_path
