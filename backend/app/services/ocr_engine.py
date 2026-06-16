"""
OCR 识别引擎服务
基于 PaddleOCR v2.9 实现中文化学题目识别
"""
import json
import logging
import numpy as np
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

# 全局 PaddleOCR 实例（启动时加载）
_paddle_ocr = None


def _get_ocr():
    """获取 PaddleOCR 实例（懒加载，使用轻量模型）"""
    global _paddle_ocr
    if _paddle_ocr is None:
        try:
            from paddleocr import PaddleOCR
            logger.info("开始加载 PaddleOCR 模型（轻量版）...")
            _paddle_ocr = PaddleOCR(
                lang='ch',
                use_angle_cls=False,  # 关闭方向分类，减少内存
                det=True,
                rec=True,
                cls=False,
                det_model_dir=None,  # 使用默认轻量模型
                rec_model_dir=None,
                show_log=False,
            )
            logger.info("PaddleOCR 轻量模型加载完成")
        except Exception as e:
            logger.error(f"PaddleOCR 模型加载失败: {e}")
            raise
    return _paddle_ocr


async def recognize_image(image_path: str) -> dict:
    """
    识别图片中的化学题目

    参数:
        image_path: 本地图片路径

    返回:
        {
            "latex": "识别出的文本（含LaTeX标记）",
            "text": "纯文本结果",
            "raw_json": "...",
            "confidence": 0.92,
            "engine": "paddleocr",
            "images": []
        }
    """
    try:
        return await _recognize_local(image_path)
    except Exception as e:
        logger.error(f"OCR 识别失败: {e}")
        return {
            "latex": "",
            "text": "",
            "raw_json": json.dumps({"error": str(e)}),
            "confidence": 0.0,
            "engine": "paddleocr-error",
            "images": [],
        }


async def _recognize_local(image_path: str) -> dict:
    """使用本地 PaddleOCR 识别"""
    import os

    if not os.path.exists(image_path):
        logger.error(f"图片文件不存在: {image_path}")
        return {"latex": "", "text": "", "raw_json": "{}", "confidence": 0.0, "engine": "error", "images": []}

    ocr = _get_ocr()
    logger.info(f"开始识别图片: {image_path}")

    # PaddleOCR v2 的 ocr 方法接受文件路径
    result = ocr.ocr(image_path, cls=False)
    logger.info(f"OCR 返回结果: type={type(result)}, len={len(result) if result else 0}")

    latex_parts = []
    text_parts = []
    scores = []
    elements = []

    if result and result[0]:
        for line in result[0]:
            if len(line) >= 2:
                bbox = line[0]
                text_info = line[1]
                text = text_info[0] if isinstance(text_info, (list, tuple)) else str(text_info)
                score = text_info[1] if isinstance(text_info, (list, tuple)) and len(text_info) > 1 else 0.0

                if not text:
                    continue

                element = {
                    "type": "text",
                    "text": text,
                    "score": round(float(score), 3),
                    "bbox": bbox,
                }
                elements.append(element)

                # 化学公式用 $ 包裹（简单启发式：含下标/上标/特殊符号）
                if any(c in text for c in ['²', '³', '⁺', '⁻', '₂', '₃', '→', '←', '↑', '↓', '\\']):
                    latex_parts.append(f"${text}$")
                else:
                    latex_parts.append(text)

                text_parts.append(text)
                scores.append(float(score))

    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    return {
        "latex": "\n\n".join(latex_parts),
        "text": "\n\n".join(text_parts),
        "raw_json": json.dumps({"elements": len(elements), "engine": "paddleocr"}),
        "confidence": avg_score,
        "engine": "paddleocr",
        "images": [],  # PaddleOCR v2 暂不支持图片区域裁剪
    }


async def preprocess_image(image_path: str) -> str:
    """
    图片预处理：增强对比度、去噪
    返回处理后的图片路径
    """
    from PIL import ImageEnhance, ImageFilter

    img = Image.open(image_path)
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)

    processed_path = image_path.replace(".", "_processed.")
    img.save(processed_path, quality=95)
    return processed_path
