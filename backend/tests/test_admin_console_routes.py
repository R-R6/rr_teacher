import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ADMIN_CONSOLE_API = BACKEND_DIR / "app" / "api" / "admin_console.py"
MAIN_FILE = BACKEND_DIR / "app" / "main.py"


class AdminConsoleRouteTests(unittest.TestCase):
    def test_admin_console_routes_are_registered(self):
        source = MAIN_FILE.read_text(encoding="utf-8")
        self.assertIn("admin_console", source)
        self.assertIn("app.include_router(admin_console.router, prefix=\"/api/admin\"", source)

    def test_admin_console_exposes_first_phase_endpoints(self):
        source = ADMIN_CONSOLE_API.read_text(encoding="utf-8")
        self.assertIn("@router.get(\"/me\"", source)
        self.assertIn("@router.get(\"/dashboard/summary\"", source)
        self.assertIn("@router.get(\"/dashboard/ocr-trend\"", source)
        self.assertIn("@router.get(\"/questions\"", source)
        self.assertIn("@router.get(\"/ocr-records\"", source)
        self.assertIn("@router.get(\"/cost/ocr-usage\"", source)
        self.assertIn("@router.get(\"/system/status\"", source)

    def test_admin_console_ocr_records_supports_date_range_filters(self):
        source = ADMIN_CONSOLE_API.read_text(encoding="utf-8")
        self.assertIn("date_from: str | None = Query(None)", source)
        self.assertIn("date_to: str | None = Query(None)", source)
        self.assertIn("OcrRecord.created_at >=", source)
        self.assertIn("OcrRecord.created_at <", source)

    def test_admin_console_questions_supports_author_keyword_and_tag_filter(self):
        source = ADMIN_CONSOLE_API.read_text(encoding="utf-8")
        self.assertIn("author_keyword: str | None = Query(None)", source)
        self.assertIn("tag_id: str | None = Query(None)", source)
        self.assertIn("User.username.contains(author_keyword)", source)
        self.assertIn("Question.id.in_(", source)

    def test_admin_console_question_update_flushes_deleted_tag_relations_before_reinsert(self):
        source = ADMIN_CONSOLE_API.read_text(encoding="utf-8")
        function_block = source.split('async def update_admin_question(', 1)[1].split('@router.delete("/questions/{question_id}"', 1)[0]
        self.assertIn("for rel in old_rels:", function_block)
        self.assertIn("await db.delete(rel)", function_block)
        self.assertIn("await db.flush()", function_block)


if __name__ == "__main__":
    unittest.main()
