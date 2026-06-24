"""
OCR endpoints.
"""

import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_teacher, get_current_user
from app.config import settings
from app.database import get_db
from app.models import OcrRecord, QuestionImage, User
from app.schemas import ApiResp, OcrCorrectReq
from app.services.cos_uploader import get_cos_url, upload_to_cos
from app.services.ocr_engine import recognize_image

router = APIRouter()


SUPPORTED_ENGINES = {
    "tesseract": {
        "name": "Tesseract 本地",
        "label": "极速识别",
        "formula": False,
        "figure_region": False,
        "cost": "0",
        "note": "本地 OCR，低成本，适合作为快速草稿模式。",
    },
    "pix2text_online": {
        "name": "Pix2Text 在线",
        "label": "公式高精度",
        "formula": True,
        "figure_region": True,
        "cost": "免费额度后按平台计费",
        "note": "在线公式 OCR，适合作为对照引擎。",
    },
    "pix2text_local": {
        "name": "Pix2Text 本地",
        "label": "本地高精度",
        "formula": True,
        "figure_region": True,
        "cost": "0",
        "note": "本地推理，受云端 AVX2 限制，仅建议本地开发使用。",
    },
    "doubao_vision": {
        "name": "豆包视觉",
        "label": "大模型高精度",
        "formula": True,
        "figure_region": True,
        "cost": "按模型调用计费",
        "note": "多模态图片理解，适合化学题整页结构化抽取。",
    },
}


@router.get("/engines", response_model=ApiResp)
async def list_engines(current_user: User = Depends(get_current_user)):
    items = []
    # Filter out 'pix2text_local' as it's not for production use
    engines_to_list = {k: v for k, v in SUPPORTED_ENGINES.items() if k != "pix2text_local"}

    for key, meta in engines_to_list.items():
        info = dict(meta)
        if key == "tesseract":
            try:
                from shutil import which

                info["available"] = bool(which("tesseract")) or bool(os.environ.get("TESSERACT_PATH"))
            except Exception:
                info["available"] = False
        elif key == "pix2text_online":
            info["available"] = bool(settings.PIX2TEXT_API_TOKEN)
        elif key == "pix2text_local":
            try:
                import pix2text  # noqa: F401

                info["available"] = True
            except Exception:
                info["available"] = False
        elif key == "doubao_vision":
            info["available"] = bool(
                settings.DOUBAO_API_KEY and settings.DOUBAO_BASE_URL and settings.DOUBAO_MODEL
            )
        items.append({"id": key, **info})
    return ApiResp(data={"default": settings.OCR_DEFAULT_ENGINE, "engines": items})


@router.post("/recognize", response_model=ApiResp)
async def recognize_question(
    file: UploadFile = File(..., description="拍照/上传的图片"),
    engine: str = Form(default=None, description="OCR 引擎"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/WebP/BMP 格式图片")

    chosen_engine = (engine or settings.OCR_DEFAULT_ENGINE or "tesseract").lower()
    if chosen_engine not in SUPPORTED_ENGINES:
        raise HTTPException(status_code=400, detail=f"不支持的引擎: {chosen_engine}")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    local_path = f"./uploads/{uuid.uuid4().hex}.{ext}"
    content = await file.read()
    with open(local_path, "wb") as file_obj:
        file_obj.write(content)

    cropped_paths: list[str] = []
    try:
        cos_key = f"ocr/{current_user.id}/{uuid.uuid4().hex}.{ext}"
        origin_url = await upload_to_cos(local_path, cos_key)
        origin_preview_url = get_cos_url(origin_url)

        ocr_result = await recognize_image(local_path, chosen_engine)

        figure_images = []
        for img_info in ocr_result.get("images", []):
            if img_info.get("image_url"):
                figure_images.append(
                    {
                        "id": img_info.get("id", uuid.uuid4().hex),
                        "image_url": get_cos_url(img_info["image_url"]),
                        "image_type": img_info.get("image_type", "figure"),
                        "bbox": img_info.get("bbox"),
                    }
                )
                continue

            cropped_path = img_info.get("cropped_path", "")
            if cropped_path and os.path.exists(cropped_path):
                cropped_paths.append(cropped_path)
                img_cos_key = f"ocr/{current_user.id}/fig_{uuid.uuid4().hex}.jpg"
                img_url = await upload_to_cos(cropped_path, img_cos_key)
                figure_images.append(
                    {
                        "id": img_info.get("id", uuid.uuid4().hex),
                        "image_url": get_cos_url(img_url),
                        "image_type": img_info.get("type", "figure"),
                        "bbox": img_info.get("bbox"),
                    }
                )

        record = OcrRecord(
            user_id=current_user.id,
            origin_image_url=origin_url,
            ocr_result_raw=str(ocr_result.get("raw", "")) if ocr_result.get("raw") else None,
            ocr_result_latex=ocr_result.get("latex"),
            ocr_result_text=ocr_result.get("text"),
            ocr_engine=ocr_result.get("engine", chosen_engine),
            confidence=ocr_result.get("confidence"),
            created_at=datetime.now(),
        )
        db.add(record)
        await db.flush()

        for idx, img_info in enumerate(figure_images):
            db.add(
                QuestionImage(
                    ocr_record_id=record.id,
                    image_url=img_info["image_url"],
                    image_type=img_info.get("image_type", "figure"),
                    source_bbox=img_info.get("bbox"),
                    sort_order=idx,
                )
            )

        return ApiResp(
            message="识别完成" if not ocr_result.get("error") else f"识别部分失败: {ocr_result.get('error')}",
            data={
                "record_id": record.id,
                "origin_image_url": origin_preview_url,
                "engine": ocr_result.get("engine", chosen_engine),
                "result_latex": ocr_result.get("latex"),
                "result_text": ocr_result.get("text"),
                "confidence": ocr_result.get("confidence"),
                "images": figure_images,
                "structured": ocr_result.get("structured"),
                "error": ocr_result.get("error"),
            },
        )
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
        for path in cropped_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


@router.post("/correct", response_model=ApiResp)
async def correct_ocr_result(
    req: OcrCorrectReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(OcrRecord).where(OcrRecord.id == req.record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="OCR记录不存在")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此记录")

    corrections = record.manual_corrections or []
    corrections.append(
        {
            "corrected_at": datetime.now().isoformat(),
            "old_latex": record.ocr_result_latex,
            "new_latex": req.corrected_latex,
        }
    )
    record.manual_corrections = corrections
    record.ocr_result_latex = req.corrected_latex
    if req.corrected_text:
        record.ocr_result_text = req.corrected_text

    return ApiResp(message="修正已保存")


@router.get("/history", response_model=ApiResp)
async def get_ocr_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func

    count_stmt = select(func.count()).select_from(OcrRecord).where(OcrRecord.user_id == current_user.id)
    total = (await db.execute(count_stmt)).scalar()

    stmt = (
        select(OcrRecord)
        .where(OcrRecord.user_id == current_user.id)
        .order_by(OcrRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    items = []
    for record in records:
        img_result = await db.execute(select(QuestionImage).where(QuestionImage.ocr_record_id == record.id))
        images = [
            {"id": img.id, "url": get_cos_url(img.image_url), "type": img.image_type}
            for img in img_result.scalars().all()
        ]

        items.append(
            {
                "record_id": record.id,
                "origin_image_url": get_cos_url(record.origin_image_url),
                "result_latex": record.ocr_result_latex,
                "result_text": record.ocr_result_text,
                "engine": record.ocr_engine,
                "confidence": record.confidence,
                "images": images,
                "created_at": record.created_at.isoformat(),
            }
        )

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})