import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class AdminConsoleStaticTests(unittest.TestCase):
    def test_resolve_admin_console_dir_prefers_existing_repo_path(self):
        from app.main import _resolve_admin_console_dir

        admin_dist = BACKEND_DIR.parent / "frontend" / "admin-dist"
        if not admin_dist.is_dir():
            self.skipTest("frontend/admin-dist not built")

        resolved = _resolve_admin_console_dir()
        self.assertIsNotNone(resolved)
        self.assertTrue(Path(resolved).is_dir())
        self.assertTrue((Path(resolved) / "index.html").is_file())

    def test_admin_console_static_entry_is_served(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/admin-console/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("化学教学后台控制台", response.text)
        self.assertIn("/admin-console/admin.js", response.text)

    def test_admin_console_assets_are_served(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        js_response = client.get("/admin-console/admin.js")
        css_response = client.get("/admin-console/asset-index.css")

        self.assertEqual(js_response.status_code, 200)
        self.assertEqual(css_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
