"""
Pix2Text OCR 微服务
独立部署，提供 HTTP 接口供后端调用
"""
from io import BytesIO
from fastapi import FastAPI, UploadFile, File
from pix2text import Pix2Text

app = FastAPI(title="OCR 微服务")

# 全局 Pix2Text 实例 (启动时加载模型)
p2t = None


@app.on_event("startup")
async def load_model():
    """启动时加载 Pix2Text 模型"""
    global p2t
    p2t = Pix2Text()


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    """
    识别图片中的化学公式/文字
    返回: {latex, text, confidence}
    """
    content = await file.read()

    # Pix2Text 识别
    result = p2t.recognize(BytesIO(content), file_type="page")

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

    return {
        "latex": "\n\n".join(latex_parts),
        "text": "\n\n".join(text_parts),
        "confidence": 0.85,  # P2T 不提供全局置信度
        "engine": "pix2text",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": p2t is not None}
