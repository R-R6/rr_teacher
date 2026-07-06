import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
MODELS = BACKEND_DIR / "app" / "models.py"
OCR_QUOTA = BACKEND_DIR / "app" / "services" / "ocr_quota.py"
USAGE_PLAN_SERVICE = BACKEND_DIR / "app" / "services" / "usage_plan_service.py"
ADMIN_CONSOLE_API = BACKEND_DIR / "app" / "api" / "admin_console.py"
MIGRATIONS_DIR = BACKEND_DIR / "alembic" / "versions"


class UserUsagePlanTests(unittest.TestCase):
    def test_user_usage_plan_model_is_persisted(self):
        source = MODELS.read_text(encoding="utf-8")

        self.assertIn("class UserUsagePlan", source)
        self.assertIn('__tablename__ = "user_usage_plan"', source)
        self.assertIn("daily_ocr_limit", source)
        self.assertIn("monthly_ocr_limit", source)
        self.assertIn("uq_user_usage_plan_user", source)

    def test_user_usage_plan_migration_exists(self):
        migration_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(MIGRATIONS_DIR.glob("*.py"))
        )

        self.assertIn('"user_usage_plan"', migration_source)
        self.assertIn('"plan_code"', migration_source)
        self.assertIn('"daily_ocr_limit"', migration_source)
        self.assertIn('"monthly_ocr_limit"', migration_source)

    def test_ocr_quota_service_resolves_user_specific_limits(self):
        quota_source = OCR_QUOTA.read_text(encoding="utf-8")
        plan_source = USAGE_PLAN_SERVICE.read_text(encoding="utf-8")

        self.assertIn("get_effective_ocr_quota_limits", quota_source)
        self.assertIn("UserUsagePlan", plan_source)
        self.assertIn("monthly_limit", quota_source)

    def test_admin_console_exposes_user_usage_and_quota_routes(self):
        source = ADMIN_CONSOLE_API.read_text(encoding="utf-8")

        self.assertIn('@router.get("/users/{user_id}/ocr-usage"', source)
        self.assertIn('@router.put("/users/{user_id}/quota-profile"', source)
        self.assertIn("UserQuotaProfileUpdateReq", source)


if __name__ == "__main__":
    unittest.main()
