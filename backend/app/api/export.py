"""
Word文档导出服务: 化学题目 → 标准Word试卷
处理 LaTeX 化学公式 → Word OMML公式对象
"""
import os
import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Paper, PaperItem, Question, QuestionImage
from app.schemas import ApiResp
from app.auth import get_current_user, get_current_teacher
from app.services.word_generator import generate_test_paper_word, generate_answer_sheet_word
from app.services.cos_uploader import upload_to_cos
from app.config import settings

router = APIRouter()


@router.post("/paper/{paper_id}/word", response_model=ApiResp)
async def export_paper_to_word(
    paper_id: str,
    include_answer: bool = True,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """
    将试卷导出为Word文档
    - 生成试题卷(.docx)
    - 附带生成答案卷(.docx)
    - 上传到COS并返回下载链接
    """
    # 查试卷
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出此试卷")

    # 查试卷题目
    item_result = await db.execute(
        select(PaperItem, Question)
        .join(Question, PaperItem.question_id == Question.id)
        .where(PaperItem.paper_id == paper_id)
        .order_by(PaperItem.sort_order)
    )
    rows = item_result.all()

    if not rows:
        raise HTTPException(status_code=400, detail="试卷为空")

    questions_data = []
    all_question_ids = []
    for item, q in rows:
        questions_data.append({
            "id": q.id,
            "content": q.content,
            "answer": q.answer,
            "analysis": q.analysis,
            "question_type": q.question_type,
            "options": q.options,
            "score": item.score,
            "sort_order": item.sort_order,
        })
        all_question_ids.append(q.id)

    # 构建图片映射表（从 QuestionImage 表查询）
    import httpx, re, tempfile
    image_map = {}
    if all_question_ids:
        img_result = await db.execute(
            select(QuestionImage)
            .where(QuestionImage.question_id.in_(all_question_ids))
            .order_by(QuestionImage.sort_order)
        )
        images = img_result.scalars().all()

        for img in images:
            if img.image_url:
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        img_resp = await client.get(img.image_url)
                        if img_resp.status_code == 200:
                            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                            tmp.write(img_resp.content)
                            tmp.close()
                            # OCR 引擎生成 img_001, img_002... 按 sort_order 对应
                            img_key = f"img_{img.sort_order + 1:03d}"
                            image_map[img_key] = tmp.name
                except Exception:
                    pass

    # 生成试题卷Word
    test_paper_path = generate_test_paper_word(
        paper_title=paper.title,
        paper_subtitle=paper.subtitle or "",
        total_score=paper.total_score,
        exam_duration=paper.exam_duration,
        questions=questions_data,
        image_map=image_map,
    )

    # 上传试题卷到COS
    test_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_试卷.docx"
    test_url = await upload_to_cos(test_paper_path, test_key)

    # 清理本地文件
    os.remove(test_paper_path)

    answer_url = None
    if include_answer:
        answer_path = generate_answer_sheet_word(
            paper_title=paper.title,
            questions=questions_data,
        )
        answer_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_答案.docx"
        answer_url = await upload_to_cos(answer_path, answer_key)
        os.remove(answer_path)

    # 更新试卷的Word URL
    paper.word_url = test_url
    paper.answer_word_url = answer_url

    return ApiResp(
        message="Word导出成功",
        data={
            "paper_id": paper_id,
            "test_paper_url": test_url,
            "answer_sheet_url": answer_url,
        }
    )


@router.post("/questions/word", response_model=ApiResp)
async def export_questions_to_word(
    question_ids: list[str],
    title: str = "课后练习",
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """
    直接导出选定题目为Word文档（不经过试卷）
    适合快速导出几道题打印
    """
    result = await db.execute(
        select(Question).where(Question.id.in_(question_ids))
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(status_code=400, detail="未找到指定题目")

    questions_data = []
    for idx, q in enumerate(questions):
        questions_data.append({
            "id": q.id,
            "content": q.content,
            "answer": q.answer,
            "analysis": q.analysis,
            "question_type": q.question_type,
            "options": q.options,
            "score": 5,
            "sort_order": idx + 1,
        })

    file_path = generate_test_paper_word(
        paper_title=title,
        paper_subtitle="",
        total_score=len(questions_data) * 5,
        exam_duration=45,
        questions=questions_data,
    )

    cos_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_题目.docx"
    download_url = await upload_to_cos(file_path, cos_key)
    os.remove(file_path)

    return ApiResp(message="导出成功", data={"word_url": download_url})
