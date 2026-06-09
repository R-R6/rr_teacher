"""
学生端 - 错题本 API
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models import User, MistakeBook, Question, QuestionTagRel, QuestionTag
from app.schemas import ApiResp
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=ApiResp)
async def list_mistakes(
    knowledge_point: str = Query(None, description="按知识点筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取错题列表"""
    conditions = [MistakeBook.student_id == current_user.id]

    # 构建查询
    stmt = (
        select(MistakeBook, Question)
        .join(Question, MistakeBook.question_id == Question.id)
        .where(and_(*conditions))
        .order_by(MistakeBook.last_wrong_at.desc())
    )

    # 总数
    count_stmt = (
        select(func.count())
        .select_from(MistakeBook)
        .where(and_(*conditions))
    )
    total = (await db.execute(count_stmt)).scalar()

    # 分页
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for mistake, question in rows:
        # 加载该题的标签
        tag_rows = await db.execute(
            select(QuestionTag.name, QuestionTag.tag_type)
            .join(QuestionTagRel, QuestionTag.id == QuestionTagRel.tag_id)
            .where(QuestionTagRel.question_id == question.id)
        )
        tags = [{"name": t[0], "type": t[1]} for t in tag_rows]

        items.append({
            "id": mistake.id,
            "question_id": question.id,
            "content": question.content[:100],
            "question_type": question.question_type,
            "difficulty": question.difficulty,
            "options": question.options,
            "answer": question.answer,
            "analysis": question.analysis,
            "tags": tags,
            "wrong_count": mistake.wrong_count,
            "is_mastered": mistake.is_mastered,
            "notes": mistake.notes,
            "last_wrong_at": mistake.last_wrong_at.isoformat() if mistake.last_wrong_at else None,
        })

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.post("", response_model=ApiResp)
async def add_mistake(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加错题（练习时答错自动调用）"""
    # 检查题目是否存在
    q_result = await db.execute(select(Question).where(Question.id == question_id))
    if not q_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="题目不存在")

    # 检查是否已存在
    existing = await db.execute(
        select(MistakeBook).where(
            and_(
                MistakeBook.student_id == current_user.id,
                MistakeBook.question_id == question_id,
            )
        )
    )
    record = existing.scalar_one_or_none()

    if record:
        # 已存在，增加错误次数
        record.wrong_count += 1
        record.last_wrong_at = datetime.now(timezone.utc)
        record.is_mastered = False  # 重新标记为未掌握
    else:
        # 新增
        record = MistakeBook(
            student_id=current_user.id,
            question_id=question_id,
            wrong_count=1,
            last_wrong_at=datetime.now(timezone.utc),
        )
        db.add(record)

    await db.flush()
    return ApiResp(message="已添加到错题本")


@router.put("/{mistake_id}/master", response_model=ApiResp)
async def mark_mastered(
    mistake_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记错题已掌握"""
    result = await db.execute(
        select(MistakeBook).where(
            and_(
                MistakeBook.id == mistake_id,
                MistakeBook.student_id == current_user.id,
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="错题不存在")

    record.is_mastered = True
    return ApiResp(message="已标记为掌握")


@router.delete("/{mistake_id}", response_model=ApiResp)
async def delete_mistake(
    mistake_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """从错题本删除"""
    result = await db.execute(
        select(MistakeBook).where(
            and_(
                MistakeBook.id == mistake_id,
                MistakeBook.student_id == current_user.id,
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="错题不存在")

    await db.delete(record)
    return ApiResp(message="已从错题本删除")


@router.put("/{mistake_id}/notes", response_model=ApiResp)
async def update_notes(
    mistake_id: str,
    notes: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新错题笔记"""
    result = await db.execute(
        select(MistakeBook).where(
            and_(
                MistakeBook.id == mistake_id,
                MistakeBook.student_id == current_user.id,
            )
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="错题不存在")

    record.notes = notes
    return ApiResp(message="笔记已更新")


@router.get("/stats", response_model=ApiResp)
async def get_mistake_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取错题统计"""
    # 总错题数
    total = (await db.execute(
        select(func.count())
        .select_from(MistakeBook)
        .where(MistakeBook.student_id == current_user.id)
    )).scalar() or 0

    # 已掌握数
    mastered = (await db.execute(
        select(func.count())
        .select_from(MistakeBook)
        .where(
            and_(
                MistakeBook.student_id == current_user.id,
                MistakeBook.is_mastered == True,
            )
        )
    )).scalar() or 0

    return ApiResp(data={
        "total": total,
        "mastered": mastered,
        "unmastered": total - mastered,
    })
