import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
QUESTIONS_API = BACKEND_DIR / "app" / "api" / "questions.py"


class QuestionsDeleteApiTests(unittest.TestCase):
    def test_delete_question_checks_references_before_delete(self):
        source = QUESTIONS_API.read_text(encoding="utf-8")
        self.assertIn("paper_ref_count", source)
        self.assertIn("mistake_ref_count", source)
        self.assertIn("practice_ref_count", source)
        self.assertIn("该题目已被试卷引用", source)
        self.assertIn("该题目已有学生作答或错题记录", source)
        self.assertGreaterEqual(source.count("await _ensure_question_deletable("), 2)


if __name__ == "__main__":
    unittest.main()
