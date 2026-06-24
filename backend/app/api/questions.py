"""
Question bank APIs.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_teacher, get_current_user
from app.database import get_db
from app.models import Question, QuestionImage, QuestionTag, QuestionTagRel, User
from app.schemas import ApiResp, QuestionCreateReq, QuestionUpdateReq
from app.services.cos_uploader import get_cos_url

router = APIRouter()


def _normalize_question_images(images: list[dict] | None) -> list[dict]:
    normalized = []
    for idx, image in enumerate(images or []):
        if not isinstance(image, dict):
            continue
        image_url = str(image.get("image_url") or image.get("url") or "").strip()
        if not image_url:
            continue
        normalized.append(
            {
                "id": image.get("id"),
                "image_url": image_url,
                "image_type": str(image.get("image_type") or image.get("type") or "figure"),
                "source_bbox": image.get("bbox") or image.get("source_bbox"),
                "sort_order": idx,
            }
        )
    return normalized


async def _load_question_tags(db: AsyncSession, question_id: str) -> list[dict]:
    tag_result = await db.execute(
        select(QuestionTag).join(QuestionTagRel).where(QuestionTagRel.question_id == question_id)
    )
    return [{"id": tag.id, "name": tag.name, "tag_type": tag.tag_type} for tag in tag_result.scalars().all()]


async def _load_question_images(db: AsyncSession, question_id: str) -> list[dict]:
    image_result = await db.execute(
        select(QuestionImage)
        .where(QuestionImage.question_id == question_id)
        .order_by(QuestionImage.sort_order.asc(), QuestionImage.created_at.asc())
    )
    return [
        {
            "id": image.id,
            "image_url": get_cos_url(image.image_url),
            "image_type": image.image_type,
            "source_bbox": image.source_bbox,
            "sort_order": image.sort_order,
        }
        for image in image_result.scalars().all()
    ]


async def _sync_question_images(
    db: AsyncSession,
    question_id: str,
    images: list[dict] | None,
) -> None:
    normalized_images = _normalize_question_images(images)
    if images is None:
        return

    image_ids = [item["id"] for item in normalized_images if item.get("id")]
    existing_result = await db.execute(
        select(QuestionImage).where(
            or_(
                QuestionImage.question_id == question_id,
                QuestionImage.id.in_(image_ids) if image_ids else false(),
            )
        )
    )
    existing_images = {image.id: image for image in existing_result.scalars().all()}
    current_question_image_ids = {
        image.id for image in existing_images.values() if image.question_id == question_id
    }
    kept_ids: set[str] = set()

    for item in normalized_images:
        image_id = item.get("id")
        if image_id and image_id in existing_images:
            image = existing_images[image_id]
            image.question_id = question_id
            image.image_url = item["image_url"]
            image.image_type = item["image_type"]
            image.source_bbox = item.get("source_bbox")
            image.sort_order = item["sort_order"]
            kept_ids.add(image_id)
        else:
            new_image = QuestionImage(
                question_id=question_id,
                image_url=item["image_url"],
                image_type=item["image_type"],
                source_bbox=item.get("source_bbox"),
                sort_order=item["sort_order"],
            )
            db.add(new_image)

    for image_id in current_question_image_ids - kept_ids:
        await db.delete(existing_images[image_id])


@router.post("", response_model=ApiResp)
async def create_question(
    req: QuestionCreateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    question = Question(
        author_id=current_user.id,
        content=req.content,
        answer=req.answer,
        analysis=req.analysis,
        question_type=req.question_type,
        difficulty=req.difficulty,
        source=req.source,
        source_image_url=req.source_image_url,
        options=req.options,
        ocr_record_id=req.ocr_record_id,
        is_verified=req.ocr_record_id is not None,
        created_at=datetime.now(),
    )
    db.add(question)
    await db.flush()

    if req.tag_ids:
        for tag_id in req.tag_ids:
            db.add(QuestionTagRel(question_id=question.id, tag_id=tag_id))

    if req.ocr_record_id:
        from sqlalchemy import update

        if req.images is None:
            await db.execute(
                update(QuestionImage)
                .where(QuestionImage.ocr_record_id == req.ocr_record_id)
                .values(question_id=question.id)
            )

    await _sync_question_images(db, question.id, req.images)
    return ApiResp(message="题目创建成功", data={"question_id": question.id})


@router.get("/{question_id}", response_model=ApiResp)
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    if question.author_id != current_user.id and not question.is_public:
        raise HTTPException(status_code=403, detail="无权查看该题目")

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
        "tags": await _load_question_tags(db, question.id),
        "images": await _load_question_images(db, question.id),
        "created_at": question.created_at.isoformat() if question.created_at else None,
        "updated_at": question.updated_at.isoformat() if question.updated_at else None,
    }
    return ApiResp(data=resp_data)


@router.get("", response_model=ApiResp)
async def list_questions(
    keyword: str = Query(None),
    question_type: str = Query(None),
    difficulty: int = Query(None, ge=1, le=5),
    tag_ids: str = Query(None),
    is_public: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [or_(Question.author_id == current_user.id, Question.is_public.is_(True))]

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

    count_stmt = select(func.count()).select_from(Question).where(and_(*conditions))
    total = (await db.execute(count_stmt)).scalar()

    stmt = (
        select(Question)
        .where(and_(*conditions))
        .order_by(Question.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    questions = result.scalars().all()

    tags_map = {}
    if questions:
        question_ids = [question.id for question in questions]
        tag_rows = await db.execute(
            select(QuestionTagRel.question_id, QuestionTag.id, QuestionTag.name, QuestionTag.tag_type)
            .join(QuestionTag, QuestionTagRel.tag_id == QuestionTag.id)
            .where(QuestionTagRel.question_id.in_(question_ids))
        )
        for question_id, tag_id, tag_name, tag_type in tag_rows:
            tags_map.setdefault(question_id, []).append(
                {"id": tag_id, "name": tag_name, "tag_type": tag_type}
            )

    items = []
    for question in questions:
        items.append(
            {
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
                "tags": tags_map.get(question.id, []),
                "images": [],
                "created_at": question.created_at.isoformat() if question.created_at else None,
                "updated_at": question.updated_at.isoformat() if question.updated_at else None,
            }
        )

    return ApiResp(data={"total": total, "page": page, "page_size": page_size, "items": items})


@router.put("/{question_id}", response_model=ApiResp)
async def update_question(
    question_id: str,
    req: QuestionUpdateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的题目")

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
        for tag_id in req.tag_ids:
            db.add(QuestionTagRel(question_id=question_id, tag_id=tag_id))

    await _sync_question_images(db, question_id, req.images)
    return ApiResp(message="题目更新成功")


@router.delete("/{question_id}", response_model=ApiResp)
async def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
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
    result = await db.execute(
        select(Question).where(and_(Question.id.in_(ids), Question.author_id == current_user.id))
    )
    questions = result.scalars().all()
    for question in questions:
        await db.delete(question)
    return ApiResp(message=f"已删除 {len(questions)} 道题目")
