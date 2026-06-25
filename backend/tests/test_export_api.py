import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
EXPORT_API = BACKEND_DIR / "app" / "api" / "export.py"
EXPORT_SERVICE = BACKEND_DIR / "app" / "services" / "export_service.py"


class ExportApiTests(unittest.TestCase):
    def test_export_response_urls_use_backend_download_proxy(self):
        source = EXPORT_API.read_text(encoding="utf-8")
        self.assertIn("@router.get(\"/paper/{paper_id}/word/download\")", source)
        self.assertIn("_build_paper_download_url(paper_id, \"test\")", source)
        self.assertIn("_build_paper_download_url(paper_id, \"answer\")", source)
        self.assertIn("read_storage_file", source)

    def test_export_reads_question_images_from_storage_not_public_url(self):
        service_source = EXPORT_SERVICE.read_text(encoding="utf-8")
        api_source = EXPORT_API.read_text(encoding="utf-8")

        self.assertIn("read_storage_file(image.image_url)", service_source)
        self.assertIn("\"images\": image_paths_by_question.get(question.id, [])", service_source)
        self.assertNotIn("httpx.AsyncClient", service_source)
        self.assertNotIn("httpx.AsyncClient", api_source)

    def test_export_api_delegates_image_payload_work_to_service(self):
        source = EXPORT_API.read_text(encoding="utf-8")
        self.assertIn("from app.services.export_service import", source)
        self.assertNotIn("QuestionImage", source)
        self.assertNotIn("tempfile", source)


if __name__ == "__main__":
    unittest.main()
