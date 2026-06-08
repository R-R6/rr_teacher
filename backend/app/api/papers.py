"""
试卷管理模块: 手动组卷 / 智能组卷 / 试卷查询 / 删除
"""
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.database import get_db
from app.models import User, Question, Paper, PaperItem, QuestionTagRel, QuestionTag
from app.schemas import (
    PaperCreateManualReq, PaperAutoCreateReq, PaperResp, QuestionResp, ApiResp,
)
from app.auth import get_current_user, get_current_teacher

router = APIRouter()


@router.post("/manual", response_model=ApiResp)
async def create_paper_manual(
    req: PaperCreateManualReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """手动组卷: 老师勾选题目生成试卷"""
    # 创建试卷
    paper = Paper(
        author_id=current_user.id,
        title=req.title,
        subtitle=req.subtitle,
        total_score=req.total_score,
        exam_duration=req.exam_duration,
        created_at=datetime.now(),
    )
    db.add(paper)
    await db.flush()  # 确保生成paper ID

    # 添加题目
    default_score = 5.0
    for idx, qid in enumerate(req.question_ids):
        score = req.scores[idx] if req.scores and idx < len(req.scores) else default_score
        item = PaperItem(
            paper_id=paper.id,
            question_id=qid,
            sort_order=idx + 1,
            score=score,
        )
        db.add(item)

    return ApiResp(message="试卷创建成功", data={"paper_id": paper.id})


@router.post("/auto", response_model=ApiResp)
async def create_paper_auto(
    req: PaperAutoCreateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """
    智能组卷: 按规则自动选题
    每条规则: {question_type: "choice", difficulty_min: 1, difficulty_max: 3, count: 10, score_per_question: 3}
    """
    paper = Paper(
        author_id=current_user.id,
        title=req.title,
        subtitle=req.subtitle,
        filter_params={"rules": req.rules, "tag_ids": req.tag_ids},
        total_score=req.total_score,
        exam_duration=req.exam_duration,
        created_at=datetime.now(),
    )
    db.add(paper)

    selected_question_ids = []
    sort_order = 0

    for rule in req.rules:
        q_type = rule.get("question_type", "choice")
        d_min = rule.get("difficulty_min", 1)
        d_max = rule.get("difficulty_max", 5)
        count = rule.get("count", 5)
        score_per = rule.get("score_per_question", 5)

        # 构建查询条件
        conditions = [
            or_(
                Question.author_id == current_user.id,
                Question.is_public == True,
            ),
            Question.question_type == q_type,
            Question.difficulty >= d_min,
            Question.difficulty <= d_max,
        ]

        # 限定知识点
        if req.tag_ids:
            conditions.append(
                Question.id.in_(
                    select(QuestionTagRel.question_id).where(
                        QuestionTagRel.tag_id.in_(req.tag_ids)
                    )
                )
            )

        # 查询候选题目
        stmt = select(Question).where(and_(*conditions))
        result = await db.execute(stmt)
        candidates = result.scalars().all()

        if len(candidates) < count:
            raise HTTPException(
                status_code=400,
                detail=f"{q_type} 题型候选题目不足: 需要{count}道, 仅有{len(candidates)}道"
            )

        # 随机选取
        chosen = random.sample(candidates, count)
        for q in chosen:
            sort_order += 1
            selected_question_ids.append(q.id)
            item = PaperItem(
                paper_id=paper.id,
                question_id=q.id,
                sort_order=sort_order,
                score=score_per,
            )
            db.add(item)

    await db.flush()  # 确保生成ID

    return ApiResp(
        message=f"智能组卷完成，共选取{sort_order}道题目",
        data={"paper_id": paper.id, "question_count": sort_order}
    )


@router.get("", response_model=ApiResp)
async def list_papers(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """试卷列表"""
    count_stmt = (
        select(func.count())
        .select_from(Paper)
        .where(Paper.author_id == current_user.id)
    )
    total = (await db.execute(count_stmt)).scalar()

    stmt = (
        select(Paper)
        .where(Paper.author_id == current_user.id)
        .order_by(Paper.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    papers = result.scalars().all()

    items = []
    if papers:
        paper_ids = [p.id for p in papers]
        count_result = await db.execute(
            select(PaperItem.paper_id, func.count())
            .where(PaperItem.paper_id.in_(paper_ids))
            .group_by(PaperItem.paper_id)
        )
        count_map = dict(count_result.all())
    else:
        count_map = {}

    for p in papers:
        items.append({
            "id": p.id,
            "title": p.title,
            "subtitle": p.subtitle,
            "total_score": p.total_score,
            "exam_duration": p.exam_duration,
            "question_count": count_map.get(p.id, 0),
            "word_url": p.word_url,
            "answer_word_url": p.answer_word_url,
            "created_at": p.created_at.isoformat(),
        })

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/{paper_id}", response_model=ApiResp)
async def get_paper_detail(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """试卷详情(含题目列表)"""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此试卷")

    # 加载题目
    item_result = await db.execute(
        select(PaperItem, Question)
        .join(Question, PaperItem.question_id == Question.id)
        .where(PaperItem.paper_id == paper_id)
        .order_by(PaperItem.sort_order)
    )
    rows = item_result.all()

    questions = []
    for item, q in rows:
        q_data = {
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
            "tags": [],
            "created_at": q.created_at.isoformat() if q.created_at else None,
            "updated_at": q.updated_at.isoformat() if q.updated_at else None,
            "score": item.score,
            "sort_order": item.sort_order,
        }
        questions.append(q_data)

    # 批量加载题目标签
    if questions:
        q_ids = [q["id"] for q in questions]
        tag_rows = await db.execute(
            select(QuestionTagRel.question_id, QuestionTag.id, QuestionTag.name, QuestionTag.tag_type)
            .join(QuestionTag, QuestionTagRel.tag_id == QuestionTag.id)
            .where(QuestionTagRel.question_id.in_(q_ids))
        )
        tags_map = {}
        for qid, tid, tname, ttype in tag_rows:
            if qid not in tags_map:
                tags_map[qid] = []
            tags_map[qid].append({"id": tid, "name": tname, "tag_type": ttype})
        for q_data in questions:
            q_data["tags"] = tags_map.get(q_data["id"], [])

    return ApiResp(data={
        "id": paper.id,
        "title": paper.title,
        "subtitle": paper.subtitle,
        "total_score": paper.total_score,
        "exam_duration": paper.exam_duration,
        "word_url": paper.word_url,
        "answer_word_url": paper.answer_word_url,
        "questions": questions,
        "created_at": paper.created_at.isoformat(),
    })


@router.delete("/{paper_id}", response_model=ApiResp)
async def delete_paper(
    paper_id: str,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """删除试卷"""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if paper.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此试卷")

    await db.delete(paper)
    return ApiResp(message="试卷已删除")
