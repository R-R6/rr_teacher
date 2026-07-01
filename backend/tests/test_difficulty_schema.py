import unittest

from pydantic import ValidationError

from app.schemas import QuestionCreateReq


class DifficultySchemaTests(unittest.TestCase):
    def test_question_create_accepts_custom_difficulty_level_above_five(self):
        req = QuestionCreateReq(content="question", difficulty=6)

        self.assertEqual(req.difficulty, 6)

    def test_question_create_rejects_unbounded_difficulty_level(self):
        with self.assertRaises(ValidationError):
            QuestionCreateReq(content="question", difficulty=21)


if __name__ == "__main__":
    unittest.main()
