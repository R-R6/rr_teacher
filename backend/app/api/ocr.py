"""
OCR 识别模块: 拍照上传 → 预处理 → 识别 → 结果返回
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, OcrRecord
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
    3. 调用OCR引擎识别
    4. 返回LaTeX格式结果
    """
    # 校验文件类型
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/WebP/BMP 格式图片")

    # 保存临时文件
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    local_path = f"./uploads/{uuid.uuid4().hex}.{ext}"
    content = await file.read()
    with open(local_path, "wb") as f:
        f.write(content)

    try:
        # 上传原图到COS
        cos_key = f"ocr/{current_user.id}/{uuid.uuid4().hex}.{ext}"
        origin_url = await upload_to_cos(local_path, cos_key)

        # 调用OCR识别
        ocr_result = await recognize_image(local_path)

        # 创建OCR记录
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

        return ApiResp(
            message="识别完成",
            data={
                "record_id": record.id,
                "origin_image_url": origin_url,
                "result_latex": ocr_result.get("latex"),
                "result_text": ocr_result.get("text"),
                "confidence": ocr_result.get("confidence"),
            }
        )
    finally:
        # 清理本地临时文件
        if os.path.exists(local_path):
            os.remove(local_path)


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

    # 保存修正记录
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

    # 总数
    count_stmt = select(func.count()).select_from(OcrRecord).where(OcrRecord.user_id == current_user.id)
    total = (await db.execute(count_stmt)).scalar()

    # 分页
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
        items.append({
            "record_id": r.id,
            "origin_image_url": r.origin_image_url,
            "result_latex": r.ocr_result_latex,
            "result_text": r.ocr_result_text,
            "confidence": r.confidence,
            "has_question": False,  # 是否已转为题目(需查Question表)
            "created_at": r.created_at.isoformat(),
        })

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})
