"""
Doubao vision OCR adapter.

Uses an OpenAI-compatible multimodal chat endpoint and normalizes the result
into the OCR shape used by this project.
"""

import base64
import json
import mimetypes
import re
from typing import Any

from app.config import settings


SYSTEM_PROMPT = """
You extract high-school chemistry questions from a single image.

Return JSON only. Do not wrap the result in markdown unless required by the API.
Never invent unreadable content.
If a field is uncertain, use null, empty array, or "unknown".
If the image contains figures, flowcharts, or apparatus that should be preserved as an image,
set figure_analysis.should_keep_original=true.

Required top-level JSON fields:
- question_type_guess
- question_text
- options
- formulas
- figure_analysis
- blocks
- needs_human_review
- review_notes
- overall_confidence
""".strip()


def _guess_mime_type(image_path: str) -> str:
    mime, _ = mimetypes.guess_type(image_path)
    return mime or "image/jpeg"


def image_to_data_uri(image_path: str) -> str:
    with open(image_path, "rb") as file_obj:
        encoded = base64.b64encode(file_obj.read()).decode("ascii")
    mime_type = _guess_mime_type(image_path)
    return f"data:{mime_type};base64,{encoded}"


def extract_json_payload(raw_content: str) -> dict[str, Any]:
    text = (raw_content or "").strip()
    if not text:
        raise ValueError("Empty Doubao response content")

    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not find JSON object in response: {raw_content[:300]}")

    return json.loads(text[start : end + 1])


def _normalize_options(options: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    if not isinstance(options, list):
        return normalized
    for idx, item in enumerate(options):
        if isinstance(item, dict):
            label = str(item.get("label") or chr(ord("A") + idx))
            text = str(item.get("text") or "").strip()
        else:
            label = chr(ord("A") + idx)
            text = str(item).strip()

        # Strip existing label like "A.", "B.", "C.", etc. from the beginning of the text
        text = re.sub(r"^[A-Z][.．]\s*", "", text, count=1)

        normalized.append({"label": label, "text": text})
    return normalized


def _normalize_formulas(formulas: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    if not isinstance(formulas, list):
        return normalized
    for item in formulas:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "source_text": str(item.get("source_text") or "").strip(),
                "latex": str(item.get("latex") or "").strip(),
                "confidence": float(item.get("confidence") or 0.0),
            }
        )
    return normalized


def _normalize_blocks(blocks: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    if not isinstance(blocks, list):
        return normalized
    for item in blocks:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "type": str(item.get("type") or "text"),
                "content": str(item.get("content") or "").strip(),
                "latex": item.get("latex"),
            }
        )
    return normalized


def normalize_structured_ocr(payload: dict[str, Any]) -> dict[str, Any]:
    question_text = str(payload.get("question_text") or "").strip()
    options = _normalize_options(payload.get("options"))
    formulas = _normalize_formulas(payload.get("formulas"))
    blocks = _normalize_blocks(payload.get("blocks"))
    figure_analysis = payload.get("figure_analysis") if isinstance(payload.get("figure_analysis"), dict) else {
        "has_figure": False,
        "should_keep_original": False,
        "description": "",
        "extractable": True,
    }

    review_notes = payload.get("review_notes")
    if not isinstance(review_notes, list):
        review_notes = []

    rendered_segments: list[str] = []
    if blocks:
        for block in blocks:
            block_text = str(block.get("latex") or block.get("content") or "").strip()
            if block_text:
                rendered_segments.append(block_text)
    else:
        if question_text:
            rendered_segments.append(question_text)
        for option in options:
            if option["text"]:
                rendered_segments.append(f'{option["label"]}. {option["text"]}')
        for formula in formulas:
            if formula["latex"]:
                rendered_segments.append(formula["latex"])

    result_latex = "\n".join(segment for segment in rendered_segments if segment).strip()

    plain_segments: list[str] = []
    if question_text:
        plain_segments.append(question_text)
    for option in options:
        if option["text"]:
            plain_segments.append(f'{option["label"]}. {option["text"]}')
    result_text = "\n".join(plain_segments).strip()

    structured = {
        "question_type_guess": str(payload.get("question_type_guess") or "unknown"),
        "question_text": question_text,
        "options": options,
        "formulas": formulas,
        "figure_analysis": {
            "has_figure": bool(figure_analysis.get("has_figure")),
            "should_keep_original": bool(figure_analysis.get("should_keep_original")),
            "description": str(figure_analysis.get("description") or "").strip(),
            "extractable": bool(figure_analysis.get("extractable", True)),
        },
        "blocks": blocks,
        "needs_human_review": bool(payload.get("needs_human_review", True)),
        "review_notes": [str(note).strip() for note in review_notes if str(note).strip()],
    }

    return {
        "result_text": result_text,
        "result_latex": result_latex or result_text,
        "structured": structured,
        "confidence": float(payload.get("overall_confidence") or 0.0),
    }


async def doubao_vision_recognize(image_path: str, **options) -> dict[str, Any]:
    base_url = (settings.DOUBAO_BASE_URL or "").rstrip("/")
    api_key = settings.DOUBAO_API_KEY
    model = settings.DOUBAO_MODEL
    timeout = float(options.get("timeout") or settings.DOUBAO_TIMEOUT or 60)

    if not base_url or not api_key or not model:
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "doubao_vision",
            "images": [],
            "error": "Doubao OCR is not configured",
        }

    image_data_uri = image_to_data_uri(image_path)
    payload = {
        "model": model,
        "instructions": SYSTEM_PROMPT,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": image_data_uri,
                    },
                    {
                        "type": "input_text",
                        "text": "Extract the chemistry question from this image and return strict JSON only.",
                    },
                ],
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    endpoint = f"{base_url}/responses"
    try:
        import httpx

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        if response.status_code != 200:
            return {
                "text": "",
                "latex": "",
                "confidence": 0.0,
                "engine": "doubao_vision",
                "images": [],
                "error": f"Doubao API {response.status_code}: {response.text[:500]}",
            }

        data = response.json()
        raw_content = (
            data.get("output_text")
            or _extract_text_from_output(data.get("output"))
            or ""
        )
        parsed = extract_json_payload(raw_content)
        normalized = normalize_structured_ocr(parsed)
        return {
            "text": normalized["result_text"],
            "latex": normalized["result_latex"],
            "confidence": normalized["confidence"],
            "engine": "doubao_vision",
            "images": [],
            "structured": normalized["structured"],
            "raw": {
                "provider": "doubao",
                "request": {
                    "model": model,
                    "prompt_version": settings.DOUBAO_PROMPT_VERSION,
                },
                "response": data,
            },
        }
    except Exception as exc:
        return {
            "text": "",
            "latex": "",
            "confidence": 0.0,
            "engine": "doubao_vision",
            "images": [],
            "error": f"Doubao call failed: {repr(exc)}",
        }


def _extract_text_from_output(output: Any) -> str:
    if not isinstance(output, list):
        return ""

    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    return "\n".join(parts).strip()