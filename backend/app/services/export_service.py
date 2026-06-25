"""Service helpers for Word export preparation."""
import logging
import os
import tempfile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PaperItem, Question, QuestionImage
from app.services.cos_uploader import read_storage_file

logger = logging.getLogger(__name__)


def image_temp_suffix(filename: str) -> str:
    suffix = os.path.splitext(filename or "")[1].lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
        return suffix
    return ".jpg"


def write_temp_image_file(image_bytes: bytes, filename: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=image_temp_suffix(filename), delete=False)
    try:
        tmp.write(image_bytes)
        return tmp.name
    finally:
        tmp.close()


async def load_question_image_paths(
    db: AsyncSession,
    question_ids: list[str],
) -> tuple[dict[str, list[str]], list[str]]:
    if not question_ids:
        return {}, []

    img_result = await db.execute(
        select(QuestionImage)
        .where(QuestionImage.question_id.in_(question_ids))
        .order_by(
            QuestionImage.question_id,
            QuestionImage.sort_order.asc(),
            QuestionImage.created_at.asc(),
        )
    )

    image_paths_by_question: dict[str, list[str]] = {}
    temp_paths: list[str] = []
    for image in img_result.scalars().all():
        if not image.image_url:
            continue
        try:
            image_bytes, filename = read_storage_file(image.image_url)
            temp_path = write_temp_image_file(image_bytes, filename)
        except FileNotFoundError as exc:
            logger.warning("Question image missing during Word export: %s", exc)
            continue
        except Exception as exc:
            logger.warning("Question image unreadable during Word export: %s", exc)
            continue

        temp_paths.append(temp_path)
        image_paths_by_question.setdefault(image.question_id, []).append(temp_path)

    return image_paths_by_question, temp_paths


def cleanup_temp_files(paths: list[str]) -> None:
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def paper_question_payload(
    item: PaperItem,
    question: Question,
    image_paths_by_question: dict[str, list[str]],
) -> dict:
    return {
        "id": question.id,
        "content": question.content,
        "answer": question.answer,
        "analysis": question.analysis,
        "question_type": question.question_type,
        "options": question.options,
        "score": item.score,
        "sort_order": item.sort_order,
        "images": image_paths_by_question.get(question.id, []),
    }


def selected_question_payload(
    question: Question,
    sort_order: int,
    image_paths_by_question: dict[str, list[str]],
) -> dict:
    return {
        "id": question.id,
        "content": question.content,
        "answer": question.answer,
        "analysis": question.analysis,
        "question_type": question.question_type,
        "options": question.options,
        "score": 5,
        "sort_order": sort_order,
        "images": image_paths_by_question.get(question.id, []),
    }
