import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
QUESTIONS_API = BACKEND_DIR / "app" / "api" / "questions.py"


class QuestionsApiTests(unittest.TestCase):
    def test_questions_api_delegates_image_helpers_to_service(self):
        source = QUESTIONS_API.read_text(encoding="utf-8")
        self.assertIn("from app.services.question_service import", source)
        self.assertNotIn("def _normalize_question_images", source)
        self.assertNotIn("def _sync_question_images", source)

    def test_questions_api_keeps_question_tag_model_for_list_query(self):
        source = QUESTIONS_API.read_text(encoding="utf-8")
        self.assertIn("QuestionTag", source)
        self.assertIn("QuestionTagRel", source)

    def test_question_update_flushes_deleted_tag_relations_before_reinsert(self):
        source = QUESTIONS_API.read_text(encoding="utf-8")
        function_block = source.split("async def update_question(", 1)[1].split("@router.delete", 1)[0]
        self.assertIn("for rel in old_rels:", function_block)
        self.assertIn("await db.delete(rel)", function_block)
        self.assertIn("await db.flush()", function_block)


if __name__ == "__main__":
    unittest.main()
