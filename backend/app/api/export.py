"""
Word document export endpoints.

The mini program cannot reliably access private COS files directly, so exports
are generated on the backend, stored through the configured storage adapter, and
downloaded again through backend proxy endpoints when needed.
"""
import os
import re
import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_teacher
from app.database import get_db
from app.models import Paper, PaperItem, Question, User
from app.schemas import ApiResp
from app.services.cos_uploader import get_cos_url, read_storage_file, upload_to_cos
from app.services.export_service import (
    cleanup_temp_files,
    load_question_image_paths,
    paper_question_payload,
    selected_question_payload,
)
from app.services.word_generator import generate_answer_sheet_word, generate_test_paper_word

router = APIRouter()
WORD_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _build_export_download_url(stored_url: str | None) -> str | None:
    if not stored_url:
        return None
    return get_cos_url(stored_url, expires=3600)


def _build_paper_download_url(paper_id: str, kind: str) -> str:
    return f"/api/export/paper/{paper_id}/word/download?kind={kind}"


def _build_word_filename(title: str | None, suffix: str) -> str:
    safe_title = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", title or "\u8bd5\u5377").strip(" _")
    if not safe_title:
        safe_title = "\u8bd5\u5377"
    return f"{safe_title[:50]}_{suffix}.docx"


@router.post("/paper/{paper_id}/word", response_model=ApiResp)
async def export_paper_to_word(
    paper_id: str,
    include_answer: bool = True,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """Export a paper to Word and return mini-program friendly download URLs."""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="\u8bd5\u5377\u4e0d\u5b58\u5728")
    if paper.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="\u65e0\u6743\u5bfc\u51fa\u6b64\u8bd5\u5377")

    item_result = await db.execute(
        select(PaperItem, Question)
        .join(Question, PaperItem.question_id == Question.id)
        .where(PaperItem.paper_id == paper_id)
        .order_by(PaperItem.sort_order)
    )
    rows = item_result.all()
    if not rows:
        raise HTTPException(status_code=400, detail="\u8bd5\u5377\u4e3a\u7a7a")

    all_question_ids = [q.id for _, q in rows]
    image_paths_by_question, temp_image_paths = await load_question_image_paths(db, all_question_ids)
    questions_data = [
        paper_question_payload(item, question, image_paths_by_question)
        for item, question in rows
    ]

    answer_url = None
    try:
        test_paper_path = generate_test_paper_word(
            paper_title=paper.title,
            paper_subtitle=paper.subtitle or "",
            total_score=paper.total_score,
            exam_duration=paper.exam_duration,
            questions=questions_data,
        )
        try:
            test_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_\u8bd5\u5377.docx"
            test_url = await upload_to_cos(test_paper_path, test_key)
        finally:
            os.remove(test_paper_path)

        if include_answer:
            answer_path = generate_answer_sheet_word(
                paper_title=paper.title,
                questions=questions_data,
            )
            try:
                answer_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_\u7b54\u6848.docx"
                answer_url = await upload_to_cos(answer_path, answer_key)
            finally:
                os.remove(answer_path)
    finally:
        cleanup_temp_files(temp_image_paths)

    paper.word_url = test_url
    paper.answer_word_url = answer_url
    await db.commit()

    return ApiResp(
        message="Word\u5bfc\u51fa\u6210\u529f",
        data={
            "paper_id": paper_id,
            "test_paper_url": _build_paper_download_url(paper_id, "test"),
            "answer_sheet_url": _build_paper_download_url(paper_id, "answer") if answer_url else None,
        },
    )


@router.get("/paper/{paper_id}/word/download")
async def download_paper_word(
    paper_id: str,
    kind: str = "test",
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """Download an exported Word file through the backend domain for mini program sharing."""
    if kind not in {"test", "answer"}:
        raise HTTPException(status_code=400, detail="\u65e0\u6548\u7684\u6587\u4ef6\u7c7b\u578b")

    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="\u8bd5\u5377\u4e0d\u5b58\u5728")
    if paper.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="\u65e0\u6743\u4e0b\u8f7d\u6b64\u8bd5\u5377")

    stored_url = paper.answer_word_url if kind == "answer" else paper.word_url
    if not stored_url:
        raise HTTPException(status_code=404, detail="Word\u6587\u4ef6\u672a\u751f\u6210")

    try:
        file_bytes, _ = read_storage_file(stored_url)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Word\u6587\u4ef6\u4e0d\u5b58\u5728")

    suffix = "\u7b54\u6848" if kind == "answer" else "\u8bd5\u5377"
    filename = _build_word_filename(paper.title, suffix)
    quoted_filename = quote(filename)
    return Response(
        content=file_bytes,
        media_type=WORD_MIME,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}",
            "Cache-Control": "private, max-age=300",
        },
    )


@router.post("/questions/word", response_model=ApiResp)
async def export_questions_to_word(
    question_ids: list[str],
    title: str = "\u8bfe\u540e\u7ec3\u4e60",
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """Export selected questions directly to a Word document."""
    result = await db.execute(select(Question).where(Question.id.in_(question_ids)))
    questions = result.scalars().all()
    if not questions:
        raise HTTPException(status_code=400, detail="\u672a\u627e\u5230\u6307\u5b9a\u9898\u76ee")

    image_paths_by_question, temp_image_paths = await load_question_image_paths(db, [q.id for q in questions])
    questions_data = [
        selected_question_payload(question, idx + 1, image_paths_by_question)
        for idx, question in enumerate(questions)
    ]

    try:
        file_path = generate_test_paper_word(
            paper_title=title,
            paper_subtitle="",
            total_score=len(questions_data) * 5,
            exam_duration=45,
            questions=questions_data,
        )
        try:
            cos_key = f"exports/{current_user.id}/{uuid.uuid4().hex}_\u9898\u76ee.docx"
            download_url = await upload_to_cos(file_path, cos_key)
        finally:
            os.remove(file_path)
    finally:
        cleanup_temp_files(temp_image_paths)

    return ApiResp(message="\u5bfc\u51fa\u6210\u529f", data={"word_url": _build_export_download_url(download_url)})
