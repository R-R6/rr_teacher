"""
PaddleOCR 微服务
提供化学题目 OCR 识别能力
"""
from io import BytesIO
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="PaddleOCR 微服务")

# 全局 PaddleOCR 实例
ocr_engine = None
structure_engine = None


@app.on_event("startup")
async def load_model():
    """启动时加载 PaddleOCR 模型"""
    global ocr_engine, structure_engine

    # 1. 基础 OCR（文本+公式识别）
    from paddleocr import PaddleOCR
    ocr_engine = PaddleOCR(lang='ch', show_log=False)
    print("[OCR] PaddleOCR 基础模型加载完成")

    # 2. 文档结构化分析（版面+表格+公式）
    try:
        from paddleocr import PPStructureV3
        structure_engine = PPStructureV3()
        print("[OCR] PPStructureV3 文档解析模型加载完成")
    except Exception as e:
        print(f"[OCR] PPStructureV3 加载失败: {e}，将使用基础 OCR 模式")


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    """
    识别图片中的化学题目
    优先使用 PPStructureV3（版面分析+公式识别），降级到基础 OCR
    """
    content = await file.read()
    image_bytes = BytesIO(content)

    # 优先使用 PPStructureV3（支持版面分析+公式+表格）
    if structure_engine:
        return await _recognize_structure(image_bytes)
    else:
        return await _recognize_basic(image_bytes)


async def _recognize_structure(image_bytes: BytesIO) -> dict:
    """使用 PPStructureV3 文档解析（推荐）"""
    try:
        result = structure_engine.predict(image_bytes)

        latex_parts = []
        text_parts = []
        scores = []
        elements = []

        # PPStructureV3 返回的是 Markdown 格式的结果
        if hasattr(result, 'markdown'):
            markdown_text = result.markdown
            latex_parts.append(markdown_text)
            text_parts.append(markdown_text)
        elif isinstance(result, str):
            latex_parts.append(result)
            text_parts.append(result)
        elif hasattr(result, 'elements'):
            for elem in result.elements:
                elem_text = getattr(elem, 'text', '') or str(elem)
                elem_type = getattr(elem, 'type', 'text')
                elem_score = getattr(elem, 'score', 0.0)

                if not elem_text:
                    continue

                elements.append({
                    "type": str(elem_type),
                    "text": elem_text,
                    "score": round(float(elem_score), 3),
                })

                if 'formula' in str(elem_type).lower():
                    latex_parts.append(f"${elem_text}$")
                else:
                    latex_parts.append(elem_text)
                text_parts.append(elem_text)
                scores.append(float(elem_score))

        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        return {
            "latex": "\n\n".join(latex_parts) if latex_parts else "",
            "text": "\n\n".join(text_parts) if text_parts else "",
            "confidence": avg_score,
            "elements": elements,
            "engine": "paddleocr-structure",
        }
    except Exception as e:
        print(f"[OCR] PPStructureV3 识别失败: {e}，降级到基础 OCR")
        return await _recognize_basic(image_bytes)


async def _recognize_basic(image_bytes: BytesIO) -> dict:
    """使用基础 PaddleOCR（文本识别）"""
    try:
        result = ocr_engine.predict(image_bytes)

        latex_parts = []
        text_parts = []
        scores = []
        elements = []

        # PaddleOCR predict 返回的结果结构
        if result:
            # result 可能是列表或对象
            items = result if isinstance(result, list) else getattr(result, 'rec_texts', [])

            for item in items:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    # [bbox, (text, confidence)]
                    text = item[1][0] if isinstance(item[1], (list, tuple)) else str(item[1])
                    score = item[1][1] if isinstance(item[1], (list, tuple)) and len(item[1]) > 1 else 0.0
                elif hasattr(item, 'text'):
                    text = item.text
                    score = getattr(item, 'score', 0.0)
                else:
                    continue

                if not text:
                    continue

                elements.append({
                    "type": "text",
                    "text": text,
                    "score": round(float(score), 3),
                })
                latex_parts.append(text)
                text_parts.append(text)
                scores.append(float(score))

        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        return {
            "latex": "\n\n".join(latex_parts),
            "text": "\n\n".join(text_parts),
            "confidence": avg_score,
            "elements": elements,
            "engine": "paddleocr-basic",
        }
    except Exception as e:
        print(f"[OCR] 基础 OCR 识别失败: {e}")
        return {
            "latex": "",
            "text": "",
            "confidence": 0.0,
            "elements": [],
            "engine": "paddleocr-error",
            "error": str(e),
        }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "basic_model": ocr_engine is not None,
        "structure_model": structure_engine is not None,
    }
