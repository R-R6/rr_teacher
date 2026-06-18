import sys
import types
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


fake_config = types.ModuleType("app.config")
fake_config.settings = types.SimpleNamespace(
    DOUBAO_BASE_URL="",
    DOUBAO_API_KEY="",
    DOUBAO_MODEL="",
    DOUBAO_TIMEOUT=60,
    DOUBAO_PROMPT_VERSION="v1",
)
sys.modules["app.config"] = fake_config


from app.services.doubao_ocr import extract_json_payload, normalize_structured_ocr


class DoubaoOcrTests(unittest.TestCase):
    def test_extract_json_payload_from_markdown_fence(self):
        raw = """```json
{"question_text":"question body","options":[]}
```"""
        payload = extract_json_payload(raw)
        self.assertEqual(payload["question_text"], "question body")

    def test_normalize_structured_ocr_builds_compatible_fields(self):
        payload = {
            "question_type_guess": "short_answer",
            "question_text": "question body",
            "options": [],
            "formulas": [
                {
                    "source_text": "FeCl3",
                    "latex": "\\mathrm{FeCl}_3",
                    "confidence": 0.98,
                }
            ],
            "figure_analysis": {
                "has_figure": True,
                "should_keep_original": True,
                "description": "keep original figure",
                "extractable": False,
            },
            "blocks": [
                {"type": "text", "content": "question body", "latex": None},
                {"type": "formula", "content": "FeCl3", "latex": "\\mathrm{FeCl}_3"},
            ],
            "needs_human_review": True,
            "review_notes": ["keep original figure"],
            "overall_confidence": 0.87,
        }

        normalized = normalize_structured_ocr(payload)

        self.assertEqual(normalized["result_text"], "question body")
        self.assertIn("\\mathrm{FeCl}_3", normalized["result_latex"])
        self.assertEqual(normalized["structured"]["figure_analysis"]["has_figure"], True)
        self.assertEqual(normalized["structured"]["needs_human_review"], True)
        self.assertEqual(normalized["confidence"], 0.87)


if __name__ == "__main__":
    unittest.main()
