"""Admin console APIs for the personal developer dashboard."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_admin
from app.config import settings
from app.database import get_db
from app.models import OcrRecord, OcrUsageLog, Paper, PaperItem, Question, QuestionImage, QuestionTag, QuestionTagRel, User
from app.schemas import ApiResp, OcrCorrectReq, QuestionUpdateReq, TagCreateReq, TagUpdateReq, UserQuotaProfileUpdateReq
from app.services.admin_console_service import build_system_status_payload
from app.services.cos_uploader import get_cos_url
from app.services.ocr_quota import get_ocr_quota_status, paid_ocr_engines
from app.services.question_service import load_question_images, load_question_tags, sync_question_images
from app.services.usage_plan_service import (
    get_effective_ocr_quota_limits,
    serialize_user_usage_plan,
    upsert_user_usage_plan,
)

from app.api.questions import _ensure_question_deletable
from app.api.tags import get_next_sort_order, get_tag_usage_count

router = APIRouter()


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _parse_date_boundary(value: str, end: bool = False) -> datetime:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError("empty date")

    if "T" in normalized or " " in normalized:
        return datetime.fromisoformat(normalized)

    base = datetime.fromisoformat(normalized)
    return base + timedelta(days=1) if end else base


def _build_date_keys(days: int) -> list[str]:
    today = datetime.now().date()
    return [
        (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        for offset in range(days - 1, -1, -1)
    ]


def _serialize_question_row(question: Question, author: User | None, tags: list[dict], image_count: int) -> dict:
    return {
        "id": question.id,
        "author_id": question.author_id,
        "author_name": author.nickname if author and author.nickname else (author.username if author else ""),
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
        "image_count": image_count,
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "updated_at": question.updated_at.isoformat() if question.updated_at else None,
    }


def _serialize_ocr_status(record: OcrRecord) -> str:
    if record.manual_corrections:
        return "corrected"
    if not (record.ocr_result_latex or record.ocr_result_text):
        return "empty"
    return "ok"


def _serialize_usage_log(log: OcrUsageLog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "engine": log.engine,
        "usage_day": log.usage_day,
        "status": log.status,
        "error_message": log.error_message,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "updated_at": log.updated_at.isoformat() if log.updated_at else None,
    }


@router.get("/me", response_model=ApiResp)
async def get_admin_me(current_user: User = Depends(get_current_admin)):
    return ApiResp(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "nickname": current_user.nickname,
            "role": current_user.role,
        }
    )


@router.get("/dashboard/summary", response_model=ApiResp)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    today = _today_str()

    question_count = (await db.execute(select(func.count()).select_from(Question))).scalar() or 0
    tag_count = (await db.execute(select(func.count()).select_from(QuestionTag))).scalar() or 0
    paper_count = (await db.execute(select(func.count()).select_from(Paper))).scalar() or 0
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    ocr_total_today = (
        await db.execute(
            select(func.count()).select_from(OcrUsageLog).where(OcrUsageLog.usage_day == today)
        )
    ).scalar() or 0
    ocr_failed_today = (
        await db.execute(
            select(func.count()).select_from(OcrUsageLog).where(
                and_(OcrUsageLog.usage_day == today, OcrUsageLog.status == "failed")
            )
        )
    ).scalar() or 0
    unverified_count = (
        await db.execute(select(func.count()).select_from(Question).where(Question.is_verified.is_(False)))
    ).scalar() or 0

    return ApiResp(
        data={
            "question_count": question_count,
            "tag_count": tag_count,
            "paper_count": paper_count,
            "user_count": user_count,
            "ocr_total_today": ocr_total_today,
            "ocr_failed_today": ocr_failed_today,
            "unverified_question_count": unverified_count,
        }
    )


@router.get("/dashboard/ocr-trend", response_model=ApiResp)
async def get_dashboard_ocr_trend(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    date_keys = _build_date_keys(days)
    start_day = date_keys[0]
    rows = (
        await db.execute(
            select(
                OcrUsageLog.usage_day,
                OcrUsageLog.engine,
                func.count().label("total"),
                func.sum(case((OcrUsageLog.status == "failed", 1), else_=0)).label("failed"),
            )
            .where(OcrUsageLog.usage_day >= start_day)
            .group_by(OcrUsageLog.usage_day, OcrUsageLog.engine)
            .order_by(OcrUsageLog.usage_day.asc(), OcrUsageLog.engine.asc())
        )
    ).all()

    daily_map = {day: 0 for day in date_keys}
    items = []
    for usage_day, engine, total, failed in rows:
        daily_map[usage_day] = daily_map.get(usage_day, 0) + int(total or 0)
        items.append(
            {
                "usage_day": usage_day,
                "engine": engine,
                "total": int(total or 0),
                "failed": int(failed or 0),
            }
        )

    return ApiResp(
        data={
            "days": [{"date": day, "total": daily_map.get(day, 0)} for day in date_keys],
            "items": items,
        }
    )


@router.get("/dashboard/recent-risks", response_model=ApiResp)
async def get_recent_risks(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    today = _today_str()
    failed_today = (
        await db.execute(
            select(func.count()).select_from(OcrUsageLog).where(
                and_(OcrUsageLog.usage_day == today, OcrUsageLog.status == "failed")
            )
        )
    ).scalar() or 0
    unverified_count = (
        await db.execute(select(func.count()).select_from(Question).where(Question.is_verified.is_(False)))
    ).scalar() or 0
    inactive_users = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active.is_(False)))
    ).scalar() or 0

    risks = []
    if failed_today:
        risks.append(
            {
                "level": "warning",
                "title": "今日 OCR 存在失败记录",
                "detail": f"今天共有 {failed_today} 次 OCR 调用失败，需要检查引擎状态或图片质量。",
            }
        )
    if unverified_count:
        risks.append(
            {
                "level": "notice",
                "title": "存在未校对题目",
                "detail": f"当前共有 {unverified_count} 道题目尚未校对，可优先检查 OCR 入库内容。",
            }
        )
    if inactive_users:
        risks.append(
            {
                "level": "notice",
                "title": "存在被禁用账号",
                "detail": f"当前共有 {inactive_users} 个账号处于禁用状态。",
            }
        )
    if not risks:
        risks.append(
            {
                "level": "ok",
                "title": "当前没有明显风险",
                "detail": "后台未发现需要优先处理的 OCR 或内容异常。",
            }
        )

    return ApiResp(data={"items": risks})


@router.get("/questions", response_model=ApiResp)
async def list_admin_questions(
    keyword: str | None = Query(None),
    question_type: str | None = Query(None),
    difficulty: int | None = Query(None, ge=1, le=20),
    author_id: str | None = Query(None),
    author_keyword: str | None = Query(None),
    tag_id: str | None = Query(None),
    is_verified: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
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
    if difficulty is not None:
        conditions.append(Question.difficulty == difficulty)
    if author_id:
        conditions.append(Question.author_id == author_id)
    if author_keyword:
        conditions.append(
            or_(
                User.username.contains(author_keyword),
                User.nickname.contains(author_keyword),
            )
        )
    if tag_id:
        conditions.append(
            Question.id.in_(
                select(QuestionTagRel.question_id).where(QuestionTagRel.tag_id == tag_id)
            )
        )
    if is_verified is not None:
        conditions.append(Question.is_verified == is_verified)

    count_stmt = select(func.count()).select_from(Question)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Question, User)
        .join(User, Question.author_id == User.id)
        .order_by(Question.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    rows = (await db.execute(stmt)).all()

    question_ids = [question.id for question, _ in rows]
    tags_map: dict[str, list[dict]] = {}
    image_count_map: dict[str, int] = {}
    if question_ids:
        tag_rows = (
            await db.execute(
                select(QuestionTagRel.question_id, QuestionTag.id, QuestionTag.name, QuestionTag.tag_type)
                .join(QuestionTag, QuestionTagRel.tag_id == QuestionTag.id)
                .where(QuestionTagRel.question_id.in_(question_ids))
            )
        ).all()
        for qid, tag_id, name, tag_type in tag_rows:
            tags_map.setdefault(qid, []).append({"id": tag_id, "name": name, "tag_type": tag_type})

        image_rows = (
            await db.execute(
                select(QuestionImage.question_id, func.count())
                .where(QuestionImage.question_id.in_(question_ids))
                .group_by(QuestionImage.question_id)
            )
        ).all()
        image_count_map = {qid: int(count or 0) for qid, count in image_rows}

    items = [
        _serialize_question_row(question, author, tags_map.get(question.id, []), image_count_map.get(question.id, 0))
        for question, author in rows
    ]
    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/questions/{question_id}", response_model=ApiResp)
async def get_admin_question_detail(
    question_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    row = (
        await db.execute(
            select(Question, User).join(User, Question.author_id == User.id).where(Question.id == question_id)
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="题目不存在")
    question, author = row
    data = _serialize_question_row(
        question,
        author,
        await load_question_tags(db, question.id),
        len(await load_question_images(db, question.id)),
    )
    data["images"] = await load_question_images(db, question.id)
    return ApiResp(data=data)


@router.put("/questions/{question_id}", response_model=ApiResp)
async def update_admin_question(
    question_id: str,
    req: QuestionUpdateReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    update_fields = req.model_dump(exclude_unset=True, exclude={"tag_ids", "images"})
    for field, value in update_fields.items():
        setattr(question, field, value)
    question.updated_at = datetime.now()

    if req.tag_ids is not None:
        old_rels = (
            await db.execute(select(QuestionTagRel).where(QuestionTagRel.question_id == question_id))
        ).scalars().all()
        for rel in old_rels:
            await db.delete(rel)
        await db.flush()
        for tag_id in req.tag_ids:
            db.add(QuestionTagRel(question_id=question_id, tag_id=tag_id))

    await sync_question_images(db, question_id, req.images)
    return ApiResp(message="题目更新成功")


@router.delete("/questions/{question_id}", response_model=ApiResp)
async def delete_admin_question(
    question_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    question = (await db.execute(select(Question).where(Question.id == question_id))).scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    await _ensure_question_deletable(db, question_id)
    await db.delete(question)
    return ApiResp(message="题目已删除")


@router.get("/tags", response_model=ApiResp)
async def list_admin_tags(
    tag_type: str | None = Query(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(QuestionTag).order_by(QuestionTag.tag_type, QuestionTag.sort_order, QuestionTag.name)
    if tag_type:
        stmt = stmt.where(QuestionTag.tag_type == tag_type)
    tags = (await db.execute(stmt)).scalars().all()
    items = [
        {
            "id": tag.id,
            "name": tag.name,
            "tag_type": tag.tag_type,
            "parent_id": tag.parent_id,
            "sort_order": tag.sort_order,
        }
        for tag in tags
    ]
    return ApiResp(data=items)


@router.post("/tags", response_model=ApiResp)
async def create_admin_tag(
    req: TagCreateReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    exists = (await db.execute(select(QuestionTag).where(QuestionTag.name == req.name))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="标签名已存在")

    sort_order = req.sort_order if req.sort_order is not None else await get_next_sort_order(db, req.tag_type)
    tag = QuestionTag(
        name=req.name,
        tag_type=req.tag_type,
        parent_id=req.parent_id,
        sort_order=sort_order,
    )
    db.add(tag)
    await db.flush()
    return ApiResp(message="标签创建成功", data={"tag_id": tag.id})


@router.put("/tags/{tag_id}", response_model=ApiResp)
async def update_admin_tag(
    tag_id: str,
    req: TagUpdateReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    tag = (await db.execute(select(QuestionTag).where(QuestionTag.id == tag_id))).scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    duplicate = (
        await db.execute(select(QuestionTag).where(and_(QuestionTag.name == req.name, QuestionTag.id != tag_id)))
    ).scalar_one_or_none()
    if duplicate:
        raise HTTPException(status_code=400, detail="标签名已存在")

    tag.name = req.name
    if req.sort_order is not None:
        tag.sort_order = req.sort_order
    await db.flush()
    return ApiResp(message="标签更新成功", data={"tag_id": tag.id})


@router.delete("/tags/{tag_id}", response_model=ApiResp)
async def delete_admin_tag(
    tag_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    tag = (await db.execute(select(QuestionTag).where(QuestionTag.id == tag_id))).scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    usage_count = await get_tag_usage_count(db, tag_id)
    if usage_count:
        raise HTTPException(status_code=400, detail=f"该标签已被 {usage_count} 道题目使用，暂时不能删除")

    await db.delete(tag)
    return ApiResp(message="标签已删除")


@router.get("/ocr-records", response_model=ApiResp)
async def list_admin_ocr_records(
    engine: str | None = Query(None),
    user_id: str | None = Query(None),
    status: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if engine:
        conditions.append(OcrRecord.ocr_engine == engine)
    if user_id:
        conditions.append(OcrRecord.user_id == user_id)
    if date_from:
        try:
            conditions.append(OcrRecord.created_at >= _parse_date_boundary(date_from))
        except ValueError:
            raise HTTPException(status_code=400, detail="date_from 格式无效，应为 YYYY-MM-DD 或 ISO datetime")
    if date_to:
        try:
            conditions.append(OcrRecord.created_at < _parse_date_boundary(date_to, end=True))
        except ValueError:
            raise HTTPException(status_code=400, detail="date_to 格式无效，应为 YYYY-MM-DD 或 ISO datetime")
    if status == "corrected":
        conditions.append(OcrRecord.manual_corrections.is_not(None))
    elif status == "empty":
        conditions.append(
            and_(
                OcrRecord.manual_corrections.is_(None),
                OcrRecord.ocr_result_latex.is_(None),
                OcrRecord.ocr_result_text.is_(None),
            )
        )
    elif status == "ok":
        conditions.append(
            and_(
                OcrRecord.manual_corrections.is_(None),
                or_(OcrRecord.ocr_result_latex.is_not(None), OcrRecord.ocr_result_text.is_not(None)),
            )
        )

    count_stmt = select(func.count()).select_from(OcrRecord)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(OcrRecord, User)
        .join(User, OcrRecord.user_id == User.id)
        .order_by(OcrRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    rows = (await db.execute(stmt)).all()

    record_ids = [record.id for record, _ in rows]
    image_count_map: dict[str, int] = {}
    if record_ids:
        image_rows = (
            await db.execute(
                select(QuestionImage.ocr_record_id, func.count())
                .where(QuestionImage.ocr_record_id.in_(record_ids))
                .group_by(QuestionImage.ocr_record_id)
            )
        ).all()
        image_count_map = {record_id: int(count or 0) for record_id, count in image_rows}

    items = []
    for record, user in rows:
        derived_status = _serialize_ocr_status(record)
        items.append(
            {
                "id": record.id,
                "user_id": record.user_id,
                "username": user.username,
                "nickname": user.nickname,
                "engine": record.ocr_engine,
                "confidence": record.confidence,
                "status": derived_status,
                "origin_image_url": get_cos_url(record.origin_image_url),
                "result_text_preview": (record.ocr_result_text or record.ocr_result_latex or "")[:120],
                "image_count": image_count_map.get(record.id, 0),
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
        )

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/ocr-records/{record_id}", response_model=ApiResp)
async def get_admin_ocr_record(
    record_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    row = (
        await db.execute(select(OcrRecord, User).join(User, OcrRecord.user_id == User.id).where(OcrRecord.id == record_id))
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="OCR记录不存在")
    record, user = row

    images = (
        await db.execute(
            select(QuestionImage)
            .where(QuestionImage.ocr_record_id == record_id)
            .order_by(QuestionImage.sort_order.asc(), QuestionImage.created_at.asc())
        )
    ).scalars().all()

    return ApiResp(
        data={
            "id": record.id,
            "user_id": record.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "engine": record.ocr_engine,
            "confidence": record.confidence,
            "status": _serialize_ocr_status(record),
            "origin_image_url": get_cos_url(record.origin_image_url),
            "processed_image_url": get_cos_url(record.processed_image_url) if record.processed_image_url else "",
            "ocr_result_latex": record.ocr_result_latex,
            "ocr_result_text": record.ocr_result_text,
            "manual_corrections": record.manual_corrections or [],
            "images": [
                {
                    "id": image.id,
                    "image_url": get_cos_url(image.image_url),
                    "image_type": image.image_type,
                    "source_bbox": image.source_bbox,
                    "sort_order": image.sort_order,
                }
                for image in images
            ],
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
    )


@router.post("/ocr-records/{record_id}/correct", response_model=ApiResp)
async def correct_admin_ocr_record(
    record_id: str,
    req: OcrCorrectReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    record = (await db.execute(select(OcrRecord).where(OcrRecord.id == record_id))).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="OCR记录不存在")

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
    if req.corrected_text is not None:
        record.ocr_result_text = req.corrected_text
    return ApiResp(message="修正已保存")


@router.get("/papers", response_model=ApiResp)
async def list_admin_papers(
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if keyword:
        conditions.append(or_(Paper.title.contains(keyword), Paper.subtitle.contains(keyword)))

    count_stmt = select(func.count()).select_from(Paper)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Paper, User)
        .join(User, Paper.author_id == User.id)
        .order_by(Paper.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    rows = (await db.execute(stmt)).all()

    paper_ids = [paper.id for paper, _ in rows]
    item_count_map = {}
    if paper_ids:
        counts = (
            await db.execute(
                select(PaperItem.paper_id, func.count()).where(PaperItem.paper_id.in_(paper_ids)).group_by(PaperItem.paper_id)
            )
        ).all()
        item_count_map = {paper_id: int(count or 0) for paper_id, count in counts}

    items = [
        {
            "id": paper.id,
            "author_id": paper.author_id,
            "author_name": user.nickname or user.username,
            "title": paper.title,
            "subtitle": paper.subtitle,
            "question_count": item_count_map.get(paper.id, 0),
            "total_score": paper.total_score,
            "exam_duration": paper.exam_duration,
            "word_url": paper.word_url,
            "answer_word_url": paper.answer_word_url,
            "created_at": paper.created_at.isoformat() if paper.created_at else None,
        }
        for paper, user in rows
    ]
    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.delete("/papers/{paper_id}", response_model=ApiResp)
async def delete_admin_paper(
    paper_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    paper = (await db.execute(select(Paper).where(Paper.id == paper_id))).scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    await db.delete(paper)
    return ApiResp(message="试卷已删除")


@router.get("/users", response_model=ApiResp)
async def list_admin_users(
    keyword: str | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if keyword:
        conditions.append(
            or_(
                User.username.contains(keyword),
                User.nickname.contains(keyword),
                User.school.contains(keyword),
                User.phone.contains(keyword),
            )
        )
    if role:
        conditions.append(User.role == role)
    if is_active is not None:
        conditions.append(User.is_active == is_active)

    count_stmt = select(func.count()).select_from(User)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(User)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    users = (await db.execute(stmt)).scalars().all()

    user_ids = [user.id for user in users]
    question_counts = {}
    paper_counts = {}
    ocr_counts = {}
    if user_ids:
        question_counts = dict(
            (
                await db.execute(
                    select(Question.author_id, func.count())
                    .where(Question.author_id.in_(user_ids))
                    .group_by(Question.author_id)
                )
            ).all()
        )
        paper_counts = dict(
            (
                await db.execute(
                    select(Paper.author_id, func.count()).where(Paper.author_id.in_(user_ids)).group_by(Paper.author_id)
                )
            ).all()
        )
        ocr_counts = dict(
            (
                await db.execute(
                    select(OcrRecord.user_id, func.count()).where(OcrRecord.user_id.in_(user_ids)).group_by(OcrRecord.user_id)
                )
            ).all()
        )

    items = [
        {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role,
            "school": user.school,
            "phone": user.phone,
            "is_active": user.is_active,
            "question_count": int(question_counts.get(user.id, 0) or 0),
            "paper_count": int(paper_counts.get(user.id, 0) or 0),
            "ocr_count": int(ocr_counts.get(user.id, 0) or 0),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]
    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.get("/users/{user_id}", response_model=ApiResp)
async def get_admin_user_detail(
    user_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    question_count = (
        await db.execute(select(func.count()).select_from(Question).where(Question.author_id == user_id))
    ).scalar() or 0
    paper_count = (
        await db.execute(select(func.count()).select_from(Paper).where(Paper.author_id == user_id))
    ).scalar() or 0
    ocr_count = (
        await db.execute(select(func.count()).select_from(OcrRecord).where(OcrRecord.user_id == user_id))
    ).scalar() or 0
    quota_limits = await get_effective_ocr_quota_limits(db, user_id)
    quota_profile = serialize_user_usage_plan(quota_limits.get("profile"), quota_limits)

    return ApiResp(
        data={
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role,
            "school": user.school,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "question_count": question_count,
            "paper_count": paper_count,
            "ocr_count": ocr_count,
            "quota_profile": quota_profile,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    )


@router.get("/users/{user_id}/ocr-usage", response_model=ApiResp)
async def get_admin_user_ocr_usage(
    user_id: str,
    days: int = Query(7, ge=1, le=30),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    date_keys = _build_date_keys(days)
    start_day = date_keys[0]
    quota_limits = await get_effective_ocr_quota_limits(db, user_id)
    quota_profile = serialize_user_usage_plan(quota_limits.get("profile"), quota_limits)

    usage_total = (
        await db.execute(
            select(func.count()).select_from(OcrUsageLog).where(
                and_(OcrUsageLog.user_id == user_id, OcrUsageLog.usage_day >= start_day)
            )
        )
    ).scalar() or 0
    usage_logs = (
        await db.execute(
            select(OcrUsageLog)
            .where(and_(OcrUsageLog.user_id == user_id, OcrUsageLog.usage_day >= start_day))
            .order_by(OcrUsageLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    summary_rows = (
        await db.execute(
            select(
                OcrUsageLog.usage_day,
                OcrUsageLog.engine,
                OcrUsageLog.status,
                func.count().label("total"),
            )
            .where(and_(OcrUsageLog.user_id == user_id, OcrUsageLog.usage_day >= start_day))
            .group_by(OcrUsageLog.usage_day, OcrUsageLog.engine, OcrUsageLog.status)
            .order_by(OcrUsageLog.usage_day.asc(), OcrUsageLog.engine.asc())
        )
    ).all()

    daily_totals = {day: 0 for day in date_keys}
    engine_totals: dict[str, int] = {}
    status_totals: dict[str, int] = {}
    for usage_day, engine, status, total in summary_rows:
        total = int(total or 0)
        daily_totals[usage_day] = daily_totals.get(usage_day, 0) + total
        engine_totals[engine] = engine_totals.get(engine, 0) + total
        status_totals[status] = status_totals.get(status, 0) + total

    recent_records = (
        await db.execute(
            select(OcrRecord)
            .where(OcrRecord.user_id == user_id)
            .order_by(OcrRecord.created_at.desc())
            .limit(10)
        )
    ).scalars().all()

    paid_engine_status = []
    for engine in sorted(paid_ocr_engines()):
        paid_engine_status.append(
            {
                "engine": engine,
                **await get_ocr_quota_status(db, user_id, engine),
            }
        )

    return ApiResp(
        data={
            "user_id": user_id,
            "username": user.username,
            "days": [{"date": day, "total": daily_totals.get(day, 0)} for day in date_keys],
            "by_engine": [
                {"engine": engine, "total": total}
                for engine, total in sorted(engine_totals.items())
            ],
            "by_status": [
                {"status": status, "total": total}
                for status, total in sorted(status_totals.items())
            ],
            "quota_profile": quota_profile,
            "paid_engine_status": paid_engine_status,
            "usage_logs": [_serialize_usage_log(log) for log in usage_logs],
            "usage_total": int(usage_total or 0),
            "page": page,
            "page_size": page_size,
            "recent_ocr_records": [
                {
                    "id": record.id,
                    "engine": record.ocr_engine,
                    "status": _serialize_ocr_status(record),
                    "confidence": record.confidence,
                    "result_text_preview": (record.ocr_result_text or record.ocr_result_latex or "")[:120],
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in recent_records
            ],
        }
    )


@router.put("/users/{user_id}/quota-profile", response_model=ApiResp)
async def update_admin_user_quota_profile(
    user_id: str,
    req: UserQuotaProfileUpdateReq,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    profile = await upsert_user_usage_plan(db, user_id, req.model_dump())
    quota_limits = await get_effective_ocr_quota_limits(db, user_id)
    return ApiResp(
        message="用户套餐与 OCR 限额已更新",
        data=serialize_user_usage_plan(profile, quota_limits),
    )


@router.get("/cost/ocr-usage", response_model=ApiResp)
async def get_admin_ocr_usage(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    date_keys = _build_date_keys(days)
    start_day = date_keys[0]

    trend_rows = (
        await db.execute(
            select(
                OcrUsageLog.usage_day,
                OcrUsageLog.engine,
                func.count().label("total"),
                func.sum(case((OcrUsageLog.status == "failed", 1), else_=0)).label("failed"),
            )
            .where(OcrUsageLog.usage_day >= start_day)
            .group_by(OcrUsageLog.usage_day, OcrUsageLog.engine)
            .order_by(OcrUsageLog.usage_day.asc(), OcrUsageLog.engine.asc())
        )
    ).all()
    user_rows = (
        await db.execute(
            select(
                OcrUsageLog.user_id,
                User.username,
                func.count().label("total"),
                func.sum(case((OcrUsageLog.status == "failed", 1), else_=0)).label("failed"),
            )
            .join(User, OcrUsageLog.user_id == User.id)
            .where(OcrUsageLog.usage_day >= start_day)
            .group_by(OcrUsageLog.user_id, User.username)
            .order_by(func.count().desc(), User.username.asc())
        )
    ).all()

    engine_totals = {}
    daily_totals = {day: 0 for day in date_keys}
    for usage_day, engine, total, failed in trend_rows:
        total = int(total or 0)
        failed = int(failed or 0)
        daily_totals[usage_day] = daily_totals.get(usage_day, 0) + total
        engine_totals.setdefault(engine, {"engine": engine, "total": 0, "failed": 0})
        engine_totals[engine]["total"] += total
        engine_totals[engine]["failed"] += failed

    return ApiResp(
        data={
            "days": [{"date": day, "total": daily_totals.get(day, 0)} for day in date_keys],
            "by_engine": list(engine_totals.values()),
            "by_day_engine": [
                {
                    "usage_day": usage_day,
                    "engine": engine,
                    "total": int(total or 0),
                    "failed": int(failed or 0),
                }
                for usage_day, engine, total, failed in trend_rows
            ],
            "by_user": [
                {
                    "user_id": user_id,
                    "username": username,
                    "total": int(total or 0),
                    "failed": int(failed or 0),
                }
                for user_id, username, total, failed in user_rows
            ],
        }
    )


@router.get("/system/status", response_model=ApiResp)
async def get_admin_system_status(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    question_count = (await db.execute(select(func.count()).select_from(Question))).scalar() or 0
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    payload = build_system_status_payload(
        settings=settings,
        health_status="ok",
        question_count=int(question_count),
        user_count=int(user_count),
    )
    return ApiResp(data=payload)
