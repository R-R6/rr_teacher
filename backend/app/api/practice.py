"""
学生端 - 刷题记录 API
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from app.database import get_db
from app.models import User, PracticeRecord, Question, MistakeBook, QuestionTagRel, QuestionTag
from app.schemas import ApiResp
from app.auth import get_current_user

router = APIRouter()


@router.get("/questions", response_model=ApiResp)
async def get_practice_questions(
    mode: str = Query("sequential", description="刷题模式: sequential/random/knowledge"),
    tag_id: str = Query(None, description="按知识点筛选"),
    difficulty: int = Query(None, ge=1, le=5, description="按难度筛选"),
    count: int = Query(20, ge=1, le=100, description="题目数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取刷题题目列表
    - sequential: 顺序刷题
    - random: 随机刷题
    - knowledge: 按知识点筛选
    - mistakes: 错题重练
    """
    conditions = [
        or_(
            Question.author_id == current_user.id,
            Question.is_public == True,
        )
    ]

    if difficulty:
        conditions.append(Question.difficulty == difficulty)

    if tag_id:
        conditions.append(
            Question.id.in_(
                select(QuestionTagRel.question_id)
                .where(QuestionTagRel.tag_id == tag_id)
            )
        )

    from sqlalchemy import or_

    stmt = select(Question).where(and_(*conditions))

    if mode == "random":
        import random as rnd
        result = await db.execute(stmt)
        all_q = result.scalars().all()
        selected = rnd.sample(all_q, min(count, len(all_q)))
        questions = selected
    else:
        stmt = stmt.order_by(Question.created_at.desc()).limit(count)
        result = await db.execute(stmt)
        questions = result.scalars().all()

    items = []
    for q in questions:
        items.append({
            "id": q.id,
            "content": q.content,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "options": q.options,
            "answer": q.answer,
            "analysis": q.analysis,
            "source": q.source,
        })

    return ApiResp(data={"total": len(items), "questions": items})


@router.post("/submit", response_model=ApiResp)
async def submit_answer(
    question_id: str,
    student_answer: str = "",
    is_correct: bool = False,
    duration_seconds: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交练习答案"""
    # 验证题目存在
    q_result = await db.execute(select(Question).where(Question.id == question_id))
    if not q_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="题目不存在")

    # 保存练习记录
    record = PracticeRecord(
        student_id=current_user.id,
        question_id=question_id,
        student_answer=student_answer,
        is_correct=is_correct,
        duration_seconds=duration_seconds,
    )
    db.add(record)

    # 答错自动加入错题本
    if not is_correct:
        existing = await db.execute(
            select(MistakeBook).where(
                and_(
                    MistakeBook.student_id == current_user.id,
                    MistakeBook.question_id == question_id,
                )
            )
        )
        mistake = existing.scalar_one_or_none()
        if mistake:
            mistake.wrong_count += 1
            mistake.last_wrong_at = datetime.now(timezone.utc)
            mistake.is_mastered = False
        else:
            db.add(MistakeBook(
                student_id=current_user.id,
                question_id=question_id,
                wrong_count=1,
                last_wrong_at=datetime.now(timezone.utc),
            ))

    await db.flush()
    return ApiResp(message="答案已提交")


@router.get("/stats", response_model=ApiResp)
async def get_practice_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取练习统计概览"""
    # 总做题数
    total = (await db.execute(
        select(func.count())
        .select_from(PracticeRecord)
        .where(PracticeRecord.student_id == current_user.id)
    )).scalar() or 0

    # 正确数
    correct = (await db.execute(
        select(func.count())
        .select_from(PracticeRecord)
        .where(
            and_(
                PracticeRecord.student_id == current_user.id,
                PracticeRecord.is_correct == True,
            )
        )
    )).scalar() or 0

    # 今日做题数
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = (await db.execute(
        select(func.count())
        .select_from(PracticeRecord)
        .where(
            and_(
                PracticeRecord.student_id == current_user.id,
                PracticeRecord.created_at >= today,
            )
        )
    )).scalar() or 0

    # 总用时（分钟）
    total_time = (await db.execute(
        select(func.coalesce(func.sum(PracticeRecord.duration_seconds), 0))
        .where(PracticeRecord.student_id == current_user.id)
    )).scalar() or 0

    # 连续打卡天数（简化：连续有练习记录的天数）
    streak = 0
    check_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    for _ in range(365):  # 最多查365天
        day_count = (await db.execute(
            select(func.count())
            .select_from(PracticeRecord)
            .where(
                and_(
                    PracticeRecord.student_id == current_user.id,
                    PracticeRecord.created_at >= check_date,
                    PracticeRecord.created_at < check_date + timedelta(days=1),
                )
            )
        )).scalar() or 0
        if day_count > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    accuracy = round(correct / total * 100, 1) if total > 0 else 0

    return ApiResp(data={
        "total_questions": total,
        "correct_questions": correct,
        "accuracy": accuracy,
        "today_count": today_count,
        "total_minutes": round(total_time / 60, 1),
        "streak_days": streak,
    })


@router.get("/trend", response_model=ApiResp)
async def get_practice_trend(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取做题趋势（近N天每天的做题数和正确率）"""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - timedelta(days=days - 1)

    trend = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        next_day = day + timedelta(days=1)

        # 当天做题总数
        day_total = (await db.execute(
            select(func.count())
            .select_from(PracticeRecord)
            .where(
                and_(
                    PracticeRecord.student_id == current_user.id,
                    PracticeRecord.created_at >= day,
                    PracticeRecord.created_at < next_day,
                )
            )
        )).scalar() or 0

        # 当天正确数
        day_correct = (await db.execute(
            select(func.count())
            .select_from(PracticeRecord)
            .where(
                and_(
                    PracticeRecord.student_id == current_user.id,
                    PracticeRecord.is_correct == True,
                    PracticeRecord.created_at >= day,
                    PracticeRecord.created_at < next_day,
                )
            )
        )).scalar() or 0

        accuracy = round(day_correct / day_total * 100, 1) if day_total > 0 else 0

        trend.append({
            "date": day.strftime("%m-%d"),
            "total": day_total,
            "correct": day_correct,
            "accuracy": accuracy,
        })

    return ApiResp(data={"trend": trend})
