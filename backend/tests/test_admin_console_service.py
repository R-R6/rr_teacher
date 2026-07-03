import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class _User:
    def __init__(self, user_id: str, username: str):
        self.id = user_id
        self.username = username


class _Settings:
    DB_TYPE = "mysql"
    COS_SECRET_ID = "secret-id"
    COS_BUCKET = "chem-bucket"
    OCR_DEFAULT_ENGINE = "tesseract"
    SWAGGER_ENABLED = False
    DEBUG = False
    RATE_LIMIT_PER_MINUTE = 120
    LOGIN_RATE_LIMIT = 5


from app.services.admin_console_service import (
    build_system_status_payload,
    is_admin_user,
    parse_admin_csv,
)


class AdminConsoleServiceTests(unittest.TestCase):
    def test_parse_admin_csv_trims_blanks_and_deduplicates(self):
        parsed = parse_admin_csv("  alice, bob ,,alice , ")
        self.assertEqual(parsed, {"alice", "bob"})

    def test_is_admin_user_matches_by_id_or_username(self):
        user = _User("u-1", "alice")
        self.assertTrue(is_admin_user(user, {"u-1"}, set()))
        self.assertTrue(is_admin_user(user, set(), {"alice"}))
        self.assertFalse(is_admin_user(user, {"u-2"}, {"bob"}))

    def test_build_system_status_payload_is_sanitized(self):
        payload = build_system_status_payload(
            settings=_Settings(),
            health_status="ok",
            question_count=12,
            user_count=3,
        )

        self.assertEqual(payload["health"], "ok")
        self.assertEqual(payload["database"]["type"], "mysql")
        self.assertEqual(payload["storage"]["mode"], "cos")
        self.assertEqual(payload["storage"]["bucket"], "chem-bucket")
        self.assertEqual(payload["ocr"]["default_engine"], "tesseract")
        self.assertEqual(payload["runtime"]["question_count"], 12)
        self.assertEqual(payload["runtime"]["user_count"], 3)
        self.assertNotIn("COS_SECRET_ID", str(payload))
        self.assertNotIn("secret-id", str(payload))


if __name__ == "__main__":
    unittest.main()
