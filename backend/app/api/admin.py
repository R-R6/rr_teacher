"""
管理工具: 数据初始化（临时接口，用完删除）
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter()


@router.get("/diag/tesseract", response_model=dict)
async def diag_tesseract(current_user: User = Depends(get_current_user)):
    """诊断端点:查看 Tesseract 实际探测结果(开发用)"""
    import os
    from app.config import settings
    from app.services.ocr_engine import _detect_tesseract
    binary = _detect_tesseract()
    return {
        "settings_TESSERACT_PATH": settings.TESSERACT_PATH,
        "env_TESSERACT_PATH": os.environ.get("TESSERACT_PATH"),
        "env_TESSDATA_PREFIX": os.environ.get("TESSDATA_PREFIX"),
        "settings_TESSDATA_PREFIX": settings.TESSDATA_PREFIX,
        "detected_binary": binary,
        "binary_exists": os.path.exists(binary) if binary else None,
        "pytesseract_importable": _try_pytesseract(),
    }


def _try_pytesseract():
    try:
        import pytesseract
        return True
    except Exception as e:
        return f"FAIL: {e!r}"


@router.post("/seed-data", response_model=dict)
async def seed_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    一次性导入预置数据（标签+题目+试卷）
    仅限开发者调用，用完后删除此接口
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="仅教师可执行")

    # 读取 init.sql 中的 INSERT 语句
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "sql", "init.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # 提取所有 INSERT 语句（跳过 CREATE TABLE 和注释）
    lines = sql_content.split("\n")
    insert_lines = []
    for line in lines:
        line = line.strip()
        if line.upper().startswith("INSERT"):
            insert_lines.append(line)

    # 逐条执行
    success_count = 0
    error_count = 0
    errors = []
    for sql in insert_lines:
        try:
            await db.execute(text(sql))
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append(str(e)[:100])

    await db.commit()

    return {
        "message": f"数据导入完成",
        "total": len(insert_lines),
        "success": success_count,
        "errors": error_count,
        "error_details": errors[:5] if errors else [],
    }
