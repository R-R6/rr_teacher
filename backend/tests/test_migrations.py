import unittest
import re
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


class MigrationGovernanceTests(unittest.TestCase):
    def test_alembic_scaffold_exists(self):
        self.assertTrue((BACKEND_DIR / "alembic.ini").is_file())
        self.assertTrue((BACKEND_DIR / "alembic" / "env.py").is_file())
        self.assertTrue((BACKEND_DIR / "alembic" / "script.py.mako").is_file())
        self.assertTrue((BACKEND_DIR / "alembic" / "versions").is_dir())

    def test_alembic_env_uses_app_metadata_and_sync_url(self):
        env_py = (BACKEND_DIR / "alembic" / "env.py").read_text(encoding="utf-8")

        self.assertIn("from app.config import settings", env_py)
        self.assertIn("from app.models import Base", env_py)
        self.assertIn("target_metadata = Base.metadata", env_py)
        self.assertIn("settings.database_url_sync", env_py)

    def test_baseline_migration_covers_current_tables(self):
        version_files = sorted((BACKEND_DIR / "alembic" / "versions").glob("*.py"))
        self.assertGreaterEqual(len(version_files), 1, "at least one migration should exist")

        models_py = (BACKEND_DIR / "app" / "models.py").read_text(encoding="utf-8")
        table_names = sorted(set(re.findall(r'__tablename__\s*=\s*"([^"]+)"', models_py)))
        self.assertIn("ocr_usage_log", table_names)

        migration_sources = "\n".join(path.read_text(encoding="utf-8") for path in version_files)
        for table_name in table_names:
            with self.subTest(table=table_name):
                self.assertIn(f'"{table_name}"', migration_sources)

    def test_auto_create_tables_is_explicitly_configured(self):
        config_py = (BACKEND_DIR / "app" / "config.py").read_text(encoding="utf-8")
        database_py = (BACKEND_DIR / "app" / "database.py").read_text(encoding="utf-8")
        env_example = (BACKEND_DIR / ".env.example").read_text(encoding="utf-8")
        cloud_example = (BACKEND_DIR / ".env.cloud.example").read_text(encoding="utf-8")

        self.assertIn("AUTO_CREATE_TABLES: bool", config_py)
        self.assertIn("AUTO_CREATE_TABLES must be false when DEBUG=false", config_py)
        self.assertIn("settings.AUTO_CREATE_TABLES", database_py)
        self.assertIn("AUTO_CREATE_TABLES=true", env_example)
        self.assertIn("AUTO_CREATE_TABLES=false", cloud_example)


if __name__ == "__main__":
    unittest.main()
