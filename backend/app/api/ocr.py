"""
OCR 识别模块: 拍照上传 → 预处理 → 识别 → 结果返回
支持文字+公式+图片区域的混合识别
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, OcrRecord, QuestionImage
from app.schemas import OcrResp, OcrCorrectReq, ApiResp
from app.auth import get_current_user, get_current_teacher
from app.services.ocr_engine import recognize_image
from app.services.cos_uploader import upload_to_cos, get_cos_url

router = APIRouter()


@router.post("/recognize", response_model=ApiResp)
async def recognize_question(
    file: UploadFile = File(..., description="拍照/上传的图片"),
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """
    拍照识别化学题目
    1. 接收图片上传
    2. 存储原图到COS
    3. 调用OCR引擎识别（含图片区域裁剪）
    4. 返回LaTeX结果 + 裁剪图片URL
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/WebP/BMP 格式图片")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    local_path = f"./uploads/{uuid.uuid4().hex}.{ext}"
    content = await file.read()
    with open(local_path, "wb") as f:
        f.write(content)

    cropped_paths = []  # 需要清理的临时文件列表
    try:
        # 1. 上传原图到COS
        cos_key = f"ocr/{current_user.id}/{uuid.uuid4().hex}.{ext}"
        origin_url = await upload_to_cos(local_path, cos_key)

        # 2. 调用OCR识别（含图片区域检测）
        ocr_result = await recognize_image(local_path)

        # 3. 上传裁剪出的图片到COS
        figure_images = []
        cropped_paths = []  # 记录需要清理的临时文件
        for img_info in ocr_result.get("images", []):
            cropped_path = img_info.get("cropped_path", "")
            if cropped_path and os.path.exists(cropped_path):
                cropped_paths.append(cropped_path)
                img_cos_key = f"ocr/{current_user.id}/fig_{uuid.uuid4().hex}.jpg"
                img_url = await upload_to_cos(cropped_path, img_cos_key)
                figure_images.append({
                    "id": img_info["id"],
                    "image_url": img_url,
                    "image_type": img_info.get("type", "figure"),
                    "bbox": img_info.get("bbox"),
                })

        # 4. 创建OCR记录
        record = OcrRecord(
            user_id=current_user.id,
            origin_image_url=origin_url,
            ocr_result_raw=ocr_result.get("raw_json"),
            ocr_result_latex=ocr_result.get("latex"),
            ocr_result_text=ocr_result.get("text"),
            ocr_engine=ocr_result.get("engine", "pix2text"),
            confidence=ocr_result.get("confidence"),
            created_at=datetime.now(),
        )
        db.add(record)
        await db.flush()

        # 5. 保存图片记录到 question_image 表
        for idx, img_info in enumerate(figure_images):
            db.add(QuestionImage(
                ocr_record_id=record.id,
                image_url=img_info["image_url"],
                image_type=img_info.get("type", "figure"),
                source_bbox=img_info.get("bbox"),
                sort_order=idx,
            ))

        return ApiResp(
            message="识别完成",
            data={
                "record_id": record.id,
                "origin_image_url": origin_url,
                "result_latex": ocr_result.get("latex"),
                "result_text": ocr_result.get("text"),
                "confidence": ocr_result.get("confidence"),
                "images": figure_images,
            }
        )
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
        # 清理裁剪出的临时图片
        for p in cropped_paths:
            if os.path.exists(p):
                os.remove(p)


@router.post("/correct", response_model=ApiResp)
async def correct_ocr_result(
    req: OcrCorrectReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """OCR结果人工修正"""
    result = await db.execute(select(OcrRecord).where(OcrRecord.id == req.record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="OCR记录不存在")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此记录")

    corrections = record.manual_corrections or []
    corrections.append({
        "corrected_at": datetime.now().isoformat(),
        "old_latex": record.ocr_result_latex,
        "new_latex": req.corrected_latex,
    })
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
    """获取用户的OCR识别历史记录"""
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
    for r in records:
        # 查询关联的图片
        img_result = await db.execute(
            select(QuestionImage).where(QuestionImage.ocr_record_id == r.id)
        )
        images = [{"id": i.id, "url": i.image_url, "type": i.image_type} for i in img_result.scalars().all()]

        items.append({
            "record_id": r.id,
            "origin_image_url": r.origin_image_url,
            "result_latex": r.ocr_result_latex,
            "result_text": r.ocr_result_text,
            "confidence": r.confidence,
            "images": images,
            "created_at": r.created_at.isoformat(),
        })

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})
