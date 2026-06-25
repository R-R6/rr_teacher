"""Service helpers for question image and tag handling."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def normalize_question_images(images: list[dict] | None) -> list[dict]:
    normalized = []
    for image in images or []:
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
                "sort_order": len(normalized),
            }
        )
    return normalized


async def load_question_tags(db: "AsyncSession", question_id: str) -> list[dict]:
    from sqlalchemy import select

    from app.models import QuestionTag, QuestionTagRel

    tag_result = await db.execute(
        select(QuestionTag).join(QuestionTagRel).where(QuestionTagRel.question_id == question_id)
    )
    return [{"id": tag.id, "name": tag.name, "tag_type": tag.tag_type} for tag in tag_result.scalars().all()]


async def load_question_images(db: "AsyncSession", question_id: str) -> list[dict]:
    from sqlalchemy import select

    from app.models import QuestionImage
    from app.services.cos_uploader import get_cos_url

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


async def sync_question_images(
    db: "AsyncSession",
    question_id: str,
    images: list[dict] | None,
) -> None:
    from sqlalchemy import false, or_, select

    from app.models import QuestionImage

    normalized_images = normalize_question_images(images)
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
