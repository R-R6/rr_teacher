import unittest
import sys

for module_name in ("app.api.tags", "app.api", "app.database", "app.config"):
    sys.modules.pop(module_name, None)

from fastapi import HTTPException

from app.api.tags import delete_tag, update_tag
from app.schemas import TagCreateReq


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _CountResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class _Tag:
    def __init__(self, tag_id="tag-1", name="old-name", tag_type="book", sort_order=2):
        self.id = tag_id
        self.name = name
        self.tag_type = tag_type
        self.sort_order = sort_order
        self.parent_id = None


class _FakeDb:
    def __init__(self, execute_values):
        self.execute_values = list(execute_values)
        self.deleted = None
        self.flushed = False

    async def execute(self, _stmt):
        value = self.execute_values.pop(0)
        if isinstance(value, tuple) and value[0] == "count":
            return _CountResult(value[1])
        return _ScalarResult(value)

    async def delete(self, tag):
        self.deleted = tag

    async def flush(self):
        self.flushed = True


class TagsManagementTests(unittest.IsolatedAsyncioTestCase):
    async def test_update_tag_changes_name_and_sort_order(self):
        tag = _Tag()
        db = _FakeDb([tag, None])

        resp = await update_tag(
            "tag-1",
            TagCreateReq(name="new-name", tag_type="book", sort_order=5),
            current_user=object(),
            db=db,
        )

        self.assertEqual(tag.name, "new-name")
        self.assertEqual(tag.sort_order, 5)
        self.assertTrue(db.flushed)
        self.assertEqual(resp.data["tag_id"], "tag-1")

    async def test_delete_tag_rejects_used_tag(self):
        tag = _Tag(tag_type="knowledge")
        db = _FakeDb([tag, ("count", 3)])

        with self.assertRaises(HTTPException) as cm:
            await delete_tag("tag-1", current_user=object(), db=db)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertIsNone(db.deleted)


if __name__ == "__main__":
    unittest.main()
