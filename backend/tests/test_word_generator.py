import sys
import unittest
import base64
import tempfile
import zipfile
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.services.word_generator import generate_answer_sheet_word
from app.services.word_generator import generate_test_paper_word


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


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

    def test_generate_test_paper_word_includes_question_images(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
            image_file.write(ONE_PIXEL_PNG)
            image_path = Path(image_file.name)

        path = Path(generate_test_paper_word(
            paper_title="含图试卷",
            paper_subtitle="",
            total_score=5,
            exam_duration=45,
            questions=[
                {
                    "content": "观察下图回答问题",
                    "question_type": "short_answer",
                    "score": 5,
                    "images": [str(image_path)],
                }
            ],
        ))

        try:
            self.assertTrue(path.exists())
            with zipfile.ZipFile(path) as docx_zip:
                media_files = [
                    name for name in docx_zip.namelist()
                    if name.startswith("word/media/")
                ]
            self.assertGreaterEqual(len(media_files), 1)
        finally:
            image_path.unlink(missing_ok=True)
            path.unlink(missing_ok=True)

    def test_generate_answer_sheet_word_includes_question_images(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as image_file:
            image_file.write(ONE_PIXEL_PNG)
            image_path = Path(image_file.name)

        path = Path(generate_answer_sheet_word(
            paper_title="含图答案",
            questions=[
                {
                    "answer": "见图",
                    "analysis": "装置如图",
                    "images": [str(image_path)],
                }
            ],
        ))

        try:
            self.assertTrue(path.exists())
            with zipfile.ZipFile(path) as docx_zip:
                media_files = [
                    name for name in docx_zip.namelist()
                    if name.startswith("word/media/")
                ]
            self.assertGreaterEqual(len(media_files), 1)
        finally:
            image_path.unlink(missing_ok=True)
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
