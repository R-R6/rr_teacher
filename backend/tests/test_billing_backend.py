import unittest
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
MODELS = BACKEND_DIR / "app" / "models.py"
MAIN_FILE = BACKEND_DIR / "app" / "main.py"
MIGRATIONS_DIR = BACKEND_DIR / "alembic" / "versions"


class BillingBackendTests(unittest.TestCase):
    def test_billing_routes_are_registered(self):
        from app.main import app

        route_paths = {
            route.path
            for route in app.routes
            if hasattr(route, "path")
        }

        self.assertIn("/api/billing/seed-offer", route_paths)
        self.assertIn("/api/billing/seed-offer/claim", route_paths)
        self.assertIn("/api/billing/orders", route_paths)
        self.assertIn("/api/billing/orders/{order_id}", route_paths)
        self.assertIn("/api/billing/me/entitlements", route_paths)
        self.assertIn("/api/billing/payments/wechat/notify", route_paths)
        self.assertIn("/api/admin/billing/seed-summary", route_paths)
        self.assertIn("/api/admin/billing/orders", route_paths)
        self.assertIn("/api/admin/billing/entitlements", route_paths)

    def test_main_includes_billing_routers(self):
        source = MAIN_FILE.read_text(encoding="utf-8")

        self.assertIn("billing", source)
        self.assertIn('app.include_router(billing.router, prefix="/api/billing"', source)
        self.assertIn('app.include_router(admin_billing.router, prefix="/api/admin/billing"', source)

    def test_billing_models_are_persisted(self):
        source = MODELS.read_text(encoding="utf-8")

        self.assertIn("class BillingOffer", source)
        self.assertIn('__tablename__ = "billing_offer"', source)
        self.assertIn("class BillingEligibility", source)
        self.assertIn('__tablename__ = "billing_eligibility"', source)
        self.assertIn("class BillingOrder", source)
        self.assertIn('__tablename__ = "billing_order"', source)
        self.assertIn("class BillingEntitlement", source)
        self.assertIn('__tablename__ = "billing_entitlement"', source)
        self.assertIn("class BillingEventLog", source)
        self.assertIn('__tablename__ = "billing_event_log"', source)

    def test_billing_migration_exists(self):
        migration_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(MIGRATIONS_DIR.glob("*.py"))
        )

        self.assertIn('"billing_offer"', migration_source)
        self.assertIn('"billing_eligibility"', migration_source)
        self.assertIn('"billing_order"', migration_source)
        self.assertIn('"billing_entitlement"', migration_source)
        self.assertIn('"billing_event_log"', migration_source)


if __name__ == "__main__":
    unittest.main()
