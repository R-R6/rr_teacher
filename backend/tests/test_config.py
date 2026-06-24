import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SECRET_KEY = "dev-only-change-me-secret-key"
DEFAULT_JWT_SECRET_KEY = "dev-only-change-me-jwt-secret-key"


def _import_config_with_env(overrides: dict[str, str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(BACKEND_DIR),
            "DEBUG": "false",
            "DB_TYPE": "sqlite",
            "CORS_ORIGINS": "https://servicewechat.com",
            "SWAGGER_ENABLED": "false",
        }
    )
    env.update(overrides)

    with tempfile.TemporaryDirectory() as temp_dir:
        stub_dir = Path(temp_dir) / "pydantic_settings"
        stub_dir.mkdir()
        (stub_dir / "__init__.py").write_text(
            textwrap.dedent(
                """
                import os


                class BaseSettings:
                    def __init__(self):
                        annotations = {}
                        for cls in reversed(self.__class__.mro()):
                            annotations.update(getattr(cls, "__annotations__", {}))
                        for name, typ in annotations.items():
                            if name.startswith("_") or name in {"Config"}:
                                continue
                            default = getattr(self.__class__, name, None)
                            value = os.environ.get(name, default)
                            if typ is bool and isinstance(value, str):
                                value = value.lower() in {"1", "true", "yes", "on"}
                            elif typ is int and isinstance(value, str):
                                value = int(value)
                            setattr(self, name, value)
                """
            ),
            encoding="utf-8",
        )
        env["PYTHONPATH"] = os.pathsep.join([temp_dir, str(BACKEND_DIR)])
        return subprocess.run(
            [sys.executable, "-c", "import app.config"],
            cwd=BACKEND_DIR,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )


class ConfigTests(unittest.TestCase):
    def test_production_rejects_default_secrets(self):
        result = _import_config_with_env(
            {
                "SECRET_KEY": DEFAULT_SECRET_KEY,
                "JWT_SECRET_KEY": DEFAULT_JWT_SECRET_KEY,
            }
        )

        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("SECRET_KEY", output)
        self.assertIn("JWT_SECRET_KEY", output)

    def test_production_accepts_explicit_secrets(self):
        result = _import_config_with_env(
            {
                "SECRET_KEY": "prod-secret-key-for-runtime-validation-001",
                "JWT_SECRET_KEY": "prod-jwt-secret-key-for-runtime-validation-001",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
