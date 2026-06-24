import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.services.word_generator import generate_answer_sheet_word


class WordGeneratorTests(unittest.TestCase):
    def test_generate_answer_sheet_word_without_images(self):
        path = Path(generate_answer_sheet_word(
            paper_title="测试试卷",
            questions=[
                {
                    "answer": "A",
                    "analysis": "解析内容",
                }
            ],
        ))

        try:
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
