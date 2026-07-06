import sys
import unittest
import importlib.util
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

FIX_SCRIPT = BACKEND_DIR / "scripts" / "fix_utf8_mojibake.py"


def load_fix_script():
    spec = importlib.util.spec_from_file_location("fix_utf8_mojibake", FIX_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FixUtf8MojibakeScriptTests(unittest.TestCase):
    def test_detects_mojibake_without_matching_normal_chinese(self):
        script = load_fix_script()

        self.assertTrue(script.looks_like_mojibake("ä½\xa0å¥½"))
        self.assertTrue(script.looks_like_mojibake("é«˜ä¸­åŒ–å­¦"))
        self.assertFalse(script.looks_like_mojibake("你好"))
        self.assertFalse(script.looks_like_mojibake("北京市第一中学"))
        self.assertFalse(script.looks_like_mojibake(""))
        self.assertFalse(script.looks_like_mojibake(None))

    def test_apply_update_scoped_by_mojibake_where_clause(self):
        script = load_fix_script()

        set_expr = script.column_repair_expr_sql("nickname")
        where_expr = script.table_where_sql(["nickname", "school"])

        self.assertIn("CASE WHEN", set_expr)
        self.assertIn("REGEXP", set_expr)
        self.assertIn("ELSE nickname END", set_expr)
        self.assertIn("nickname IS NOT NULL", where_expr)
        self.assertIn("school IS NOT NULL", where_expr)


if __name__ == "__main__":
    unittest.main()
