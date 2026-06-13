"""
PaddleOCR v2 微服务
提供化学题目 OCR 识别能力
"""
from io import BytesIO
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="PaddleOCR 微服务")

# 全局 PaddleOCR 实例
ocr_engine = None


@app.on_event("startup")
async def load_model():
    """启动时加载 PaddleOCR v2 模型"""
    global ocr_engine

    from paddleocr import PaddleOCR
    ocr_engine = PaddleOCR(
        lang='ch',
        use_angle_cls=True,
        det=True,
        rec=True,
        cls=True,
        show_log=False,
    )
    print("[OCR] PaddleOCR v2.9 模型加载完成")


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    """
    识别图片中的化学题目
    PaddleOCR v2 返回格式: [[bbox, (text, confidence)], ...]
    """
    content = await file.read()
    result = ocr_engine.ocr(BytesIO(content), cls=True)

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

                # 构建元素信息
                element = {
                    "type": "text",
                    "text": text,
                    "score": round(float(score), 3),
                    "bbox": bbox,
                }
                elements.append(element)

                latex_parts.append(text)
                text_parts.append(text)
                scores.append(float(score))

    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    return {
        "latex": "\n\n".join(latex_parts),
        "text": "\n\n".join(text_parts),
        "confidence": avg_score,
        "elements": elements,
        "engine": "paddleocr-v2",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": ocr_engine is not None,
    }
