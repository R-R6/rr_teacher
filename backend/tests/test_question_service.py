import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.services.question_service import normalize_question_images


class QuestionServiceTests(unittest.TestCase):
    def test_normalize_question_images_discards_invalid_items_and_sets_sort_order(self):
        normalized = normalize_question_images([
            {"image_url": "  /a.png  "},
            None,
            {"url": "https://example.com/b.png", "type": "table", "bbox": [1, 2, 3, 4]},
            {"image_url": ""},
        ])

        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0]["image_url"], "/a.png")
        self.assertEqual(normalized[0]["image_type"], "figure")
        self.assertEqual(normalized[0]["sort_order"], 0)
        self.assertEqual(normalized[1]["image_url"], "https://example.com/b.png")
        self.assertEqual(normalized[1]["image_type"], "table")
        self.assertEqual(normalized[1]["source_bbox"], [1, 2, 3, 4])
        self.assertEqual(normalized[1]["sort_order"], 1)


if __name__ == "__main__":
    unittest.main()
