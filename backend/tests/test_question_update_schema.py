import unittest
import sys
from pathlib import Path

from pydantic import ValidationError

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import QuestionUpdateReq


class QuestionUpdateSchemaTests(unittest.TestCase):
    def test_question_update_rejects_invalid_question_type(self):
        with self.assertRaises(ValidationError):
            QuestionUpdateReq(question_type="invalid_type")

    def test_question_update_preserves_visibility_flags(self):
        req = QuestionUpdateReq(is_public=True, is_verified=True)

        payload = req.model_dump(exclude_unset=True)
        self.assertEqual(payload["is_public"], True)
        self.assertEqual(payload["is_verified"], True)


if __name__ == "__main__":
    unittest.main()
