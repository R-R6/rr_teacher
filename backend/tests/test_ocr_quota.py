import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIG = BACKEND_DIR / "app" / "config.py"
MODELS = BACKEND_DIR / "app" / "models.py"
OCR_API = BACKEND_DIR / "app" / "api" / "ocr.py"
OCR_QUOTA = BACKEND_DIR / "app" / "services" / "ocr_quota.py"


class OcrQuotaTests(unittest.TestCase):
    def test_quota_settings_are_configurable(self):
        source = CONFIG.read_text(encoding="utf-8")

        self.assertIn("OCR_PAID_ENGINES", source)
        self.assertIn("OCR_DAILY_USER_LIMIT", source)
        self.assertIn("OCR_DAILY_GLOBAL_LIMIT", source)

    def test_usage_log_model_is_persisted_by_database(self):
        source = MODELS.read_text(encoding="utf-8")

        self.assertIn("class OcrUsageLog", source)
        self.assertIn('__tablename__ = "ocr_usage_log"', source)
        self.assertIn("ix_ocr_usage_user_day_engine", source)
        self.assertIn("ix_ocr_usage_global_day_engine", source)

    def test_recognize_reserves_quota_before_paid_ocr_call(self):
        source = OCR_API.read_text(encoding="utf-8")

        self.assertIn("reserve_ocr_quota", source)
        self.assertIn("finalize_ocr_quota", source)
        self.assertLess(
            source.index("quota_log_id = await reserve_ocr_quota"),
            source.index("ocr_result = await recognize_image"),
        )

    def test_quota_service_returns_teacher_friendly_429(self):
        source = OCR_QUOTA.read_text(encoding="utf-8")

        self.assertIn("status_code=429", source)
        self.assertIn("请切换极速识别", source)
        self.assertIn("OCR_DAILY_USER_LIMIT", source)
        self.assertIn("OCR_DAILY_GLOBAL_LIMIT", source)


if __name__ == "__main__":
    unittest.main()
