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
    # 使用中文+英文配置，启用公式检测和表格识别
    text_formula_config = dict(
        languages=('en', 'ch_sim'),
        mfd=dict(model_name='mfd-1.5', model_backend='onnx'),
        formula=dict(model_name='mfr-1.5', model_backend='onnx'),
        text=dict(rec_model_name='doc-densenet_lite_666-gru_large'),
    )
    total_config = {
        'layout': {'scores_thresh': 0.45},
        'text_formula': text_formula_config,
    }
    p2t = Pix2Text(total_configs=total_config, enable_formula=True, enable_table=True, device='cpu')
    print("[OCR] Pix2Text 模型加载完成")


@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    """
    识别图片中的化学公式/文字
    返回: {latex, text, confidence, elements}
    """
    content = await file.read()

    # Pix2Text 识别（返回 Page 对象）
    page = p2t.recognize(BytesIO(content), file_type="page")

    latex_parts = []
    text_parts = []
    scores = []
    elements = []

    for elem in page.elements:
        elem_type = elem.type.value if hasattr(elem.type, 'value') else str(elem.type)
        elem_text = elem.text if hasattr(elem, 'text') else ''
        elem_score = elem.score if hasattr(elem, 'score') else 0.0

        if not elem_text:
            continue

        element_info = {"type": elem_type, "text": elem_text, "score": round(elem_score, 3)}
        elements.append(element_info)

        if elem_type in ('text', 'title', 'figure_caption', 'table_caption'):
            text_parts.append(elem_text)
            latex_parts.append(elem_text)
            scores.append(elem_score)
        elif elem_type == 'formula':
            # 公式用 $ 包裹
            latex_parts.append(f"${elem_text}$")
            text_parts.append(elem_text)
            scores.append(elem_score)
        elif elem_type == 'table':
            # 表格保留原始格式
            latex_parts.append(elem_text)
            text_parts.append(elem_text)
            scores.append(elem_score)
        else:
            # 其他类型（如 inline 公式）
            latex_parts.append(elem_text)
            text_parts.append(elem_text)
            scores.append(elem_score)

    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    return {
        "latex": "\n\n".join(latex_parts),
        "text": "\n\n".join(text_parts),
        "confidence": avg_score,
        "elements": elements,
        "engine": "pix2text",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": p2t is not None}
