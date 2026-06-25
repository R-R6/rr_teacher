import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
EXPORT_API = BACKEND_DIR / "app" / "api" / "export.py"


class ExportApiTests(unittest.TestCase):
    def test_export_response_urls_use_backend_download_proxy(self):
        source = EXPORT_API.read_text(encoding="utf-8")
        self.assertIn("@router.get(\"/paper/{paper_id}/word/download\")", source)
        self.assertIn("_build_paper_download_url(paper_id, \"test\")", source)
        self.assertIn("_build_paper_download_url(paper_id, \"answer\")", source)
        self.assertIn("read_storage_file", source)

    def test_export_reads_question_images_from_storage_not_public_url(self):
        source = EXPORT_API.read_text(encoding="utf-8")
        self.assertIn("read_storage_file(image.image_url)", source)
        self.assertIn("\"images\": image_paths_by_question.get(question.id, [])", source)
        self.assertNotIn("httpx.AsyncClient", source)


if __name__ == "__main__":
    unittest.main()
