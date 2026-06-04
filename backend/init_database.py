"""
数据库初始化脚本
创建表结构 + 初始化默认标签
"""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models import QuestionTag
from sqlalchemy import select


DEFAULT_TAGS = [
    # 教材册别
    {"name": "必修第一册", "tag_type": "book", "sort_order": 1},
    {"name": "必修第二册", "tag_type": "book", "sort_order": 2},
    {"name": "选择性必修1 化学反应原理", "tag_type": "book", "sort_order": 3},
    {"name": "选择性必修2 物质结构与性质", "tag_type": "book", "sort_order": 4},
    {"name": "选择性必修3 有机化学基础", "tag_type": "book", "sort_order": 5},
    # 题型
    {"name": "选择题", "tag_type": "type", "sort_order": 1},
    {"name": "填空题", "tag_type": "type", "sort_order": 2},
    {"name": "实验题", "tag_type": "type", "sort_order": 3},
    {"name": "计算题", "tag_type": "type", "sort_order": 4},
    {"name": "简答题", "tag_type": "type", "sort_order": 5},
    # 难度
    {"name": "极易", "tag_type": "difficulty", "sort_order": 1},
    {"name": "较易", "tag_type": "difficulty", "sort_order": 2},
    {"name": "中等", "tag_type": "difficulty", "sort_order": 3},
    {"name": "较难", "tag_type": "difficulty", "sort_order": 4},
    {"name": "极难", "tag_type": "difficulty", "sort_order": 5},
    # 知识点
    {"name": "物质的分类与转化", "tag_type": "knowledge", "sort_order": 1},
    {"name": "离子反应", "tag_type": "knowledge", "sort_order": 2},
    {"name": "氧化还原反应", "tag_type": "knowledge", "sort_order": 3},
    {"name": "钠及其化合物", "tag_type": "knowledge", "sort_order": 4},
    {"name": "氯及其化合物", "tag_type": "knowledge", "sort_order": 5},
    {"name": "铁及其化合物", "tag_type": "knowledge", "sort_order": 6},
    {"name": "物质的量", "tag_type": "knowledge", "sort_order": 7},
    {"name": "元素周期表与周期律", "tag_type": "knowledge", "sort_order": 8},
    {"name": "化学键与分子结构", "tag_type": "knowledge", "sort_order": 9},
    {"name": "化学反应与能量", "tag_type": "knowledge", "sort_order": 10},
    {"name": "化学反应速率与平衡", "tag_type": "knowledge", "sort_order": 11},
    {"name": "水溶液中的离子平衡", "tag_type": "knowledge", "sort_order": 12},
    {"name": "电化学", "tag_type": "knowledge", "sort_order": 13},
    {"name": "有机化合物", "tag_type": "knowledge", "sort_order": 14},
    {"name": "化学实验基础", "tag_type": "knowledge", "sort_order": 15},
]


async def seed_tags():
    """初始化默认标签"""
    async with AsyncSessionLocal() as session:
        for tag_data in DEFAULT_TAGS:
            result = await session.execute(
                select(QuestionTag).where(QuestionTag.name == tag_data["name"])
            )
            if not result.scalar_one_or_none():
                tag = QuestionTag(**tag_data)
                session.add(tag)
        await session.commit()
    print(f"✓ 已初始化 {len(DEFAULT_TAGS)} 个预设标签")


async def main():
    """执行初始化"""
    print("正在创建数据库表...")
    await init_db()
    print("✓ 数据库表创建完成")

    print("正在初始化预设标签...")
    await seed_tags()

    print("\n初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
