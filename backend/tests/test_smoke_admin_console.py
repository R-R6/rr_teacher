import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "scripts" / "smoke_admin_console.py"


def load_smoke_module():
    spec = importlib.util.spec_from_file_location("smoke_admin_console", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeProcess:
    def __init__(self, returncode=1):
        self.returncode = returncode

    def poll(self):
        return self.returncode


class SmokeAdminConsoleTests(unittest.TestCase):
    def test_resolve_backend_python_prefers_env_override(self):
        smoke = load_smoke_module()
        with mock.patch.dict(os.environ, {"ADMIN_SMOKE_BACKEND_PYTHON": "C:/custom/python.exe"}, clear=False):
            self.assertEqual(smoke.resolve_backend_python(), "C:/custom/python.exe")

    def test_build_backend_failure_message_includes_exit_code_and_log_tail(self):
        smoke = load_smoke_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout_path = Path(tmpdir) / "stdout.log"
            stderr_path = Path(tmpdir) / "stderr.log"
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text("No module named uvicorn\n", encoding="utf-8")

            message = smoke.build_backend_failure_message(
                FakeProcess(returncode=3),
                stdout_path,
                stderr_path,
            )

        self.assertIn("backend exited with code 3", message)
        self.assertIn("No module named uvicorn", message)


if __name__ == "__main__":
    unittest.main()
