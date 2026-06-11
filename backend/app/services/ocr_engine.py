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
    """
    使用本地 Pix2Text 库识别（降级方案）
    支持文字+公式+图片区域的混合识别
    """
    try:
        from pix2text import Pix2Text
    except ImportError:
        logger.warning("Pix2Text 未安装，OCR 识别不可用")
        return {
            "latex": "",
            "text": "",
            "raw_json": json.dumps({"error": "pix2text not installed"}),
            "confidence": 0.0,
            "engine": "unavailable",
            "images": [],
        }

    p2t = Pix2Text()
    result = p2t.recognize(image_path, file_type="page")

    latex_parts = []
    text_parts = []
    figure_images = []  # 裁剪出的图片信息
    img_counter = 0

    # Pix2Text 返回的是对象列表
    elements = []
    if hasattr(result, 'elements'):
        elements = result.elements
    elif isinstance(result, (list, tuple)):
        elements = result

    for item in elements:
        # 获取元素信息
        if hasattr(item, 'type'):
            elem_type = item.type.value if hasattr(item.type, 'value') else str(item.type)
            elem_text = item.text if hasattr(item, 'text') else ''
            elem_score = item.score if hasattr(item, 'score') else 0.0
            bbox = item.bbox if hasattr(item, 'bbox') else None
        else:
            continue

        if elem_type in ('text', 'title', 'figure_caption', 'table_caption', 'table'):
            if elem_text:
                text_parts.append(elem_text)
                latex_parts.append(elem_text)
        elif elem_type == 'formula':
            if elem_text:
                latex_parts.append(f"${elem_text}$")
                text_parts.append(elem_text)
        elif elem_type in ('figure', 'image', 'apparatus', 'structure'):
            # 图片/图表/装置图/结构式 → 从原图裁剪保存
            if bbox:
                img_counter += 1
                img_id = f"img_{img_counter:03d}"
                cropped_path = _crop_image_region(image_path, bbox)
                if cropped_path:
                    figure_images.append({
                        "id": img_id,
                        "bbox": list(bbox) if hasattr(bbox, '__iter__') else bbox,
                        "type": elem_type,
                        "cropped_path": cropped_path,
                    })
                    latex_parts.append(f"{{{{img:{img_id}}}}}")
                    text_parts.append(f"[图片:{elem_type}]")
        else:
            if elem_text:
                latex_parts.append(elem_text)
                text_parts.append(elem_text)

    latex_result = "\n\n".join(latex_parts) if latex_parts else ""
    text_result = "\n\n".join(text_parts) if text_parts else ""

    # 计算平均置信度
    scores = []
    for item in elements:
        if hasattr(item, 'score') and item.score:
            scores.append(item.score)
    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    return {
        "latex": latex_result,
        "text": text_result,
        "raw_json": json.dumps({"elements": len(elements), "figures": len(figure_images)}, ensure_ascii=False),
        "confidence": avg_score,
        "engine": "pix2text",
        "images": figure_images,
    }


def _crop_image_region(image_path: str, bbox) -> str:
    """
    根据 bbox 从原图裁剪出图片区域
    bbox: (x1, y1, x2, y2) 坐标
    返回裁剪后的图片路径
    """
    try:
        from PIL import Image

        img = Image.open(image_path)

        # 解析 bbox
        if hasattr(bbox, '__iter__') and len(bbox) >= 4:
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        else:
            return ""

        # 添加 padding（每边 5px）
        padding = 5
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(img.width, x2 + padding)
        y2 = min(img.height, y2 + padding)

        if x2 <= x1 or y2 <= y1:
            return ""

        # 裁剪
        cropped = img.crop((x1, y1, x2, y2))

        # 保存
        import uuid
        cropped_path = f"./uploads/{uuid.uuid4().hex}_fig.jpg"
        cropped.save(cropped_path, "JPEG", quality=95)

        return cropped_path
    except Exception as e:
        logger.warning(f"裁剪图片区域失败: {e}")
        return ""


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
