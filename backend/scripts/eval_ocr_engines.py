"""
Evaluate OCR engines on a directory of sample images.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import time
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.ocr_engine import recognize_image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", required=True)
    parser.add_argument("--output-dir", default=str(BACKEND_DIR / "eval_results"))
    parser.add_argument(
        "--engines",
        nargs="+",
        default=["tesseract", "pix2text_online", "doubao_vision"],
    )
    return parser.parse_args()


async def evaluate_engine(image_path: Path, engine: str) -> dict:
    start = time.perf_counter()
    result = await recognize_image(str(image_path), engine=engine)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    structured = result.get("structured") or {}
    figure_analysis = structured.get("figure_analysis") or {}
    return {
        "engine": engine,
        "sample": image_path.name,
        "latency_ms": latency_ms,
        "confidence": result.get("confidence") or 0.0,
        "result_text_length": len(result.get("text") or ""),
        "result_latex_length": len(result.get("latex") or ""),
        "has_error": bool(result.get("error")),
        "error": result.get("error") or "",
        "question_type_guess": structured.get("question_type_guess") or "unknown",
        "formula_count": len(structured.get("formulas") or []),
        "has_figure": bool(figure_analysis.get("has_figure")),
        "should_keep_original": bool(figure_analysis.get("should_keep_original")),
        "needs_human_review": bool(structured.get("needs_human_review", True)),
        "raw_result": result,
    }


async def main() -> None:
    args = parse_args()
    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    samples = sorted(
        [
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
    )
    rows: list[dict] = []

    for sample in samples:
        for engine in args.engines:
            row = await evaluate_engine(sample, engine)
            rows.append(row)
            engine_dir = raw_dir / engine
            engine_dir.mkdir(parents=True, exist_ok=True)
            with open(engine_dir / f"{sample.stem}.json", "w", encoding="utf-8") as file_obj:
                json.dump(row["raw_result"], file_obj, ensure_ascii=False, indent=2)

    csv_path = output_dir / "summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=[
                "engine",
                "sample",
                "latency_ms",
                "confidence",
                "result_text_length",
                "result_latex_length",
                "has_error",
                "error",
                "question_type_guess",
                "formula_count",
                "has_figure",
                "should_keep_original",
                "needs_human_review",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})

    md_path = output_dir / "summary.md"
    lines = [
        "# OCR Engine Evaluation",
        "",
        "| sample | engine | latency_ms | confidence | text_len | formula_count | has_figure | keep_original | human_review | error |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['sample']} | {row['engine']} | {row['latency_ms']} | {row['confidence']} | "
            f"{row['result_text_length']} | {row['formula_count']} | {row['has_figure']} | "
            f"{row['should_keep_original']} | {row['needs_human_review']} | {row['error'] or '-'} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
