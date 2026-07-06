"""
对外 API 路由聚合
"""
from fastapi import APIRouter
from app.api import auth, questions, ocr, papers, tags, export, billing

api_router = APIRouter(prefix="/api")

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(questions.router, prefix="/questions", tags=["题库管理"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR识别"])
api_router.include_router(papers.router, prefix="/papers", tags=["试卷管理"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签分类"])
api_router.include_router(export.router, prefix="/export", tags=["Word导出"])
api_router.include_router(billing.router, prefix="/billing", tags=["计费与支付"])
