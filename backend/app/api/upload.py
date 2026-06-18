"""
通用文件上传模块
提供与业务无关的图片上传能力，给"看图录入"等场景使用
"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.models import User
from app.auth import get_current_teacher
from app.schemas import ApiResp
from app.services.cos_uploader import get_cos_url, upload_to_cos

router = APIRouter()

# 允许的图片类型（与 OCR 模块保持一致）
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/heic",
    "image/heif",
}
# 文件大小上限（看图录入场景单张 20MB 足够）
MAX_IMAGE_BYTES = 20 * 1024 * 1024


@router.post("/image", response_model=ApiResp)
async def upload_image(
    file: UploadFile = File(..., description="待上传的图片"),
    purpose: str = "manual_input",
    current_user: User = Depends(get_current_teacher),
):
    """
    通用图片上传（看图录入 / 资料图 / 头像等场景共用）

    1. 校验文件类型与大小
    2. 写入本地临时文件
    3. 调用 COS 上传（未配置 COS 时降级为本地存储）
    4. 返回可访问的 URL
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"仅支持 JPG/PNG/WebP/BMP/HEIC 格式，当前类型: {file.content_type}",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"图片大小超过 {MAX_IMAGE_BYTES // 1024 // 1024}MB 限制",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="空文件")

    # 推断扩展名
    ext_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/bmp": "bmp",
        "image/heic": "heic",
        "image/heif": "heif",
    }
    ext = ext_map.get(file.content_type)
    if not ext:
        # 退化: 从文件名抽取
        ext = (file.filename or "jpg").rsplit(".", 1)[-1].lower() or "jpg"

    local_path = f"./uploads/{uuid.uuid4().hex}.{ext}"
    try:
        with open(local_path, "wb") as f:
            f.write(content)

        cos_key = f"images/{current_user.id}/{purpose}/{uuid.uuid4().hex}.{ext}"
        url = await upload_to_cos(local_path, cos_key)

        return ApiResp(
            message="上传成功",
            data={
                "url": get_cos_url(url),
                "cos_key": cos_key,
                "size": len(content),
                "content_type": file.content_type,
                "purpose": purpose,
            },
        )
    finally:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass
