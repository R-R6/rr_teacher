"""
标签分类管理模块: 增删改查、树形结构
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, QuestionTag
from app.schemas import TagCreateReq, TagResp, ApiResp
from app.auth import get_current_user, get_current_teacher

router = APIRouter()


@router.post("", response_model=ApiResp)
async def create_tag(
    req: TagCreateReq,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """创建标签"""
    # 检查重名
    result = await db.execute(select(QuestionTag).where(QuestionTag.name == req.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="标签名已存在")

    tag = QuestionTag(
        name=req.name,
        tag_type=req.tag_type,
        parent_id=req.parent_id,
        sort_order=req.sort_order,
    )
    db.add(tag)
    return ApiResp(message="标签创建成功", data={"tag_id": tag.id})


@router.get("", response_model=ApiResp)
async def list_tags(
    tag_type: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取标签列表（树形结构）
    返回嵌套的树形标签，适合前端级联选择器
    """
    conditions = []
    if tag_type:
        conditions.append(QuestionTag.tag_type == tag_type)

    stmt = select(QuestionTag).order_by(QuestionTag.tag_type, QuestionTag.sort_order)
    if conditions:
        from sqlalchemy import and_
        stmt = stmt.where(and_(*conditions))

    result = await db.execute(stmt)
    tags = result.scalars().all()

    # 构建树形结构
    tag_map = {}
    for t in tags:
        tag_resp = TagResp(
            id=t.id,
            name=t.name,
            tag_type=t.tag_type,
            parent_id=t.parent_id,
            sort_order=t.sort_order or 0,
            children=[],
        )
        tag_map[t.id] = tag_resp

    roots = []
    for t in tags:
        if t.parent_id and t.parent_id in tag_map:
            tag_map[t.parent_id].children.append(tag_map[t.id])
        else:
            roots.append(tag_map[t.id])

    return ApiResp(data=[r.model_dump() for r in roots])


@router.delete("/{tag_id}", response_model=ApiResp)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """删除标签"""
    result = await db.execute(select(QuestionTag).where(QuestionTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    await db.delete(tag)
    return ApiResp(message="标签已删除")


@router.post("/seed", response_model=ApiResp)
async def seed_default_tags(db: AsyncSession = Depends(get_db)):
    """
    初始化高中化学预设标签（首次部署后调用一次）
    """
    default_tags = [
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
        # 知识点（二级树形）
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

    for tag_data in default_tags:
        result = await db.execute(select(QuestionTag).where(QuestionTag.name == tag_data["name"]))
        if not result.scalar_one_or_none():
            tag = QuestionTag(**tag_data)
            db.add(tag)

    return ApiResp(message=f"已初始化 {len(default_tags)} 个预设标签")
