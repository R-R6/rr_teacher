import unittest
import sys

for module_name in ("app.api.tags", "app.api", "app.database", "app.config"):
    sys.modules.pop(module_name, None)

from app.api.tags import create_tag
from app.schemas import TagCreateReq


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
      return self.value


class _FakeDb:
    def __init__(self):
        self.execute_values = [None, 5]
        self.added = None
        self.flushed = False

    async def execute(self, _stmt):
        return _ScalarResult(self.execute_values.pop(0))

    def add(self, tag):
        self.added = tag

    async def flush(self):
        self.flushed = True
        self.added.id = "tag-1"


class TagsApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_tag_assigns_next_sort_order_and_returns_id(self):
        db = _FakeDb()
        req = TagCreateReq(name="easy-custom", tag_type="difficulty")

        resp = await create_tag(req, current_user=object(), db=db)

        self.assertTrue(db.flushed)
        self.assertEqual(db.added.sort_order, 6)
        self.assertEqual(resp.data["tag_id"], "tag-1")


if __name__ == "__main__":
    unittest.main()
