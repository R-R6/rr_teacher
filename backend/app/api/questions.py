"""
题库管理模块: 题目的增删改查 / 搜索 / 筛选
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.database import get_db
from app.models import User, Question, QuestionTagRel, QuestionTag
from app.schemas import (
    QuestionCreateReq, QuestionUpdateReq, QuestionResp,
    QuestionListReq, QuestionListResp, ApiResp,
)
from app.auth import get_current_user, get_current_teacher

router = APIRouter()


@router.post("", response_model=ApiResp)
async def create_question(
    req: QuestionCreateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """创建题目"""
    question = Question(
        author_id=current_user.id,
        content=req.content,
        answer=req.answer,
        analysis=req.analysis,
        question_type=req.question_type,
        difficulty=req.difficulty,
        source=req.source,
        options=req.options,
        ocr_record_id=req.ocr_record_id,
        is_verified=req.ocr_record_id is not None,  # OCR录入的题目默认标记为"待校对"
        created_at=datetime.now(),
    )
    db.add(question)
    await db.flush()  # 确保生成ID

    # 关联标签
    if req.tag_ids:
        for tag_id in req.tag_ids:
            rel = QuestionTagRel(question_id=question.id, tag_id=tag_id)
            db.add(rel)

    return ApiResp(message="题目创建成功", data={"question_id": question.id})


@router.get("/{question_id}", response_model=ApiResp)
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取题目详情"""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 权限检查: 只能看自己的或公开的
    if question.author_id != current_user.id and not question.is_public:
        raise HTTPException(status_code=403, detail="无权查看该题目")

    # 加载标签
    tag_result = await db.execute(
        select(QuestionTag).join(QuestionTagRel).where(QuestionTagRel.question_id == question.id)
    )
    tags = [{"id": t.id, "name": t.name, "tag_type": t.tag_type} for t in tag_result.scalars().all()]

    # 手动构建响应，避免懒加载问题
    resp_data = {
        "id": question.id,
        "author_id": question.author_id,
        "content": question.content,
        "answer": question.answer,
        "analysis": question.analysis,
        "question_type": question.question_type,
        "difficulty": question.difficulty,
        "source": question.source,
        "source_image_url": question.source_image_url,
        "options": question.options,
        "is_public": question.is_public,
        "is_verified": question.is_verified,
        "tags": tags,
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "updated_at": question.updated_at.isoformat() if question.updated_at else None,
    }
    return ApiResp(data=resp_data)


@router.get("", response_model=ApiResp)
async def list_questions(
    keyword: str = Query(None, description="关键词搜索"),
    question_type: str = Query(None, description="题型"),
    difficulty: int = Query(None, ge=1, le=5, description="难度"),
    tag_ids: str = Query(None, description="标签ID逗号分隔"),
    is_public: bool = Query(None, description="公开题库"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """题目列表(分页+筛选)"""
    try:
        # 基础查询: 只看自己的 + 公开的
        conditions = [
            or_(
                Question.author_id == current_user.id,
                Question.is_public == True,
            )
        ]

        if keyword:
            conditions.append(
                or_(
                    Question.content.contains(keyword),
                    Question.answer.contains(keyword),
                    Question.source.contains(keyword),
                )
            )
        if question_type:
            conditions.append(Question.question_type == question_type)
        if difficulty:
            conditions.append(Question.difficulty == difficulty)
        if is_public is not None:
            conditions.append(Question.is_public == is_public)

        # 查询总数
        count_stmt = select(func.count()).select_from(Question).where(and_(*conditions))
        total = (await db.execute(count_stmt)).scalar()

        # 分页查询
        stmt = (
            select(Question)
            .where(and_(*conditions))
            .order_by(Question.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        questions = result.scalars().all()

        items = []
        for q in questions:
            # 手动构建响应，避免懒加载问题
            item = {
                "id": q.id,
                "author_id": q.author_id,
                "content": q.content,
                "answer": q.answer,
                "analysis": q.analysis,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "source": q.source,
                "source_image_url": q.source_image_url,
                "options": q.options,
                "is_public": q.is_public,
                "is_verified": q.is_verified,
                "tags": [],  # 简化版本暂不加载标签
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "updated_at": q.updated_at.isoformat() if q.updated_at else None,
            }
            items.append(item)

        return ApiResp(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{question_id}", response_model=ApiResp)
async def update_question(
    question_id: str,
    req: QuestionUpdateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """更新题目"""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的题目")

    # 仅更新传入的字段
    update_fields = req.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_fields.items():
        setattr(question, field, value)
    question.updated_at = datetime.now()

    # 更新标签
    if req.tag_ids is not None:
        # 删除旧关联
        await db.execute(
            select(QuestionTagRel).where(QuestionTagRel.question_id == question_id)
        )
        old_rels = (await db.execute(
            select(QuestionTagRel).where(QuestionTagRel.question_id == question_id)
        )).scalars().all()
        for rel in old_rels:
            await db.delete(rel)
        # 添加新关联
        for tag_id in req.tag_ids:
            rel = QuestionTagRel(question_id=question_id, tag_id=tag_id)
            db.add(rel)

    return ApiResp(message="题目更新成功")


@router.delete("/{question_id}", response_model=ApiResp)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """删除题目"""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的题目")

    await db.delete(question)
    return ApiResp(message="题目已删除")


@router.post("/batch-delete", response_model=ApiResp)
async def batch_delete_questions(
    ids: list[str],
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """批量删除题目"""
    result = await db.execute(
        select(Question).where(
            and_(Question.id.in_(ids), Question.author_id == current_user.id)
        )
    )
    questions = result.scalars().all()
    for q in questions:
        await db.delete(q)
    return ApiResp(message=f"已删除 {len(questions)} 道题目")
