"""
Pydantic Schemas — 请求/响应数据校验
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ────────────────────────── 用户相关 ──────────────────────────

class UserRegisterReq(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码(6-64位)")
    role: str = Field(default="teacher", pattern="^(teacher|student)$", description="角色")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称/姓名")
    school: Optional[str] = Field(None, max_length=100, description="学校")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserLoginReq(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class WechatLoginReq(BaseModel):
    """微信小程序登录请求"""
    code: str = Field(..., description="wx.login()返回的code")
    nickname: Optional[str] = Field(None, description="微信昵称")
    avatar_url: Optional[str] = Field(None, description="微信头像URL")


class UserInfoResp(BaseModel):
    """用户信息响应"""
    id: str
    username: str
    role: str
    nickname: Optional[str] = None
    school: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResp(BaseModel):
    """登录token响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒
    user: UserInfoResp


class UpdateProfileReq(BaseModel):
    """更新用户信息请求"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    school: Optional[str] = None


# ────────────────────────── 题目相关 ──────────────────────────

class QuestionOption(BaseModel):
    """选择题选项"""
    label: str = Field(..., description="选项标签(A/B/C/D)")
    text: str = Field(..., description="选项内容(LaTeX格式)")


class QuestionCreateReq(BaseModel):
    """创建题目请求"""
    content: str = Field(..., min_length=1, description="题目正文(LaTeX格式)")
    answer: Optional[str] = Field(None, description="答案(LaTeX格式)")
    analysis: Optional[str] = Field(None, description="解析(LaTeX格式)")
    question_type: str = Field(
        default="choice",
        pattern="^(choice|fill|experiment|calculation|short_answer)$",
        description="题型"
    )
    difficulty: int = Field(default=3, ge=1, le=5, description="难度 1-5")
    source: Optional[str] = Field(None, max_length=200, description="题目来源")
    options: Optional[list[dict]] = Field(None, description="选择题选项")
    tag_ids: Optional[list[str]] = Field(None, description="关联标签ID列表")
    ocr_record_id: Optional[str] = Field(None, description="OCR识别记录ID")


class QuestionUpdateReq(BaseModel):
    """更新题目请求(仅需传要修改的字段)"""
    content: Optional[str] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[int] = None
    source: Optional[str] = None
    options: Optional[list[dict]] = None
    tag_ids: Optional[list[str]] = None


class QuestionResp(BaseModel):
    """题目响应"""
    id: str
    author_id: str
    content: str
    answer: Optional[str] = None
    analysis: Optional[str] = None
    question_type: str
    difficulty: int
    source: Optional[str] = None
    source_image_url: Optional[str] = None
    options: Optional[list[dict]] = None
    is_public: bool
    is_verified: bool
    tags: list[dict] = []  # [{id, name, tag_type}]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionListReq(BaseModel):
    """题目列表查询请求"""
    keyword: Optional[str] = Field(None, description="关键词搜索")
    question_type: Optional[str] = Field(None, description="题型筛选")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="难度筛选")
    tag_ids: Optional[str] = Field(None, description="标签ID(逗号分隔)")
    is_public: Optional[bool] = Field(None, description="是否公开")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


class QuestionListResp(BaseModel):
    """题目列表响应"""
    total: int
    page: int
    page_size: int
    items: list[QuestionResp]


# ────────────────────────── OCR相关 ──────────────────────────

class OcrResp(BaseModel):
    """OCR识别响应"""
    record_id: str
    origin_image_url: str
    result_latex: str
    result_text: str
    confidence: Optional[float] = None
    created_at: datetime


class OcrCorrectReq(BaseModel):
    """OCR人工修正请求"""
    record_id: str = Field(..., description="OCR记录ID")
    corrected_latex: str = Field(..., description="修正后的LaTeX")
    corrected_text: Optional[str] = Field(None, description="修正后的纯文本")


# ────────────────────────── 试卷相关 ──────────────────────────

class PaperCreateManualReq(BaseModel):
    """手动组卷请求"""
    title: str = Field(..., min_length=1, max_length=200, description="试卷标题")
    subtitle: Optional[str] = Field(None, max_length=200, description="副标题")
    question_ids: list[str] = Field(..., min_length=1, description="题目ID列表(按顺序)")
    scores: Optional[list[float]] = Field(None, description="每题分值(与question_ids对应)")
    total_score: int = Field(default=100, description="总分")
    exam_duration: int = Field(default=60, description="考试时长(分钟)")


class PaperAutoCreateReq(BaseModel):
    """智能组卷请求"""
    title: str = Field(..., min_length=1, max_length=200, description="试卷标题")
    subtitle: Optional[str] = Field(None, max_length=200, description="副标题")
    rules: list[dict] = Field(..., description="组卷规则: [{question_type, difficulty_range, count, score_per_question}]")
    tag_ids: Optional[list[str]] = Field(None, description="限定知识点标签")
    total_score: int = Field(default=100, description="总分")
    exam_duration: int = Field(default=60, description="考试时长(分钟)")


class PaperResp(BaseModel):
    """试卷响应"""
    id: str
    author_id: str
    title: str
    subtitle: Optional[str] = None
    total_score: int
    exam_duration: int
    sections: Optional[list] = None
    questions: list[QuestionResp] = []
    word_url: Optional[str] = None
    answer_word_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ────────────────────────── 标签相关 ──────────────────────────

class TagCreateReq(BaseModel):
    """创建标签请求"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名")
    tag_type: str = Field(..., pattern="^(book|knowledge|type|difficulty)$", description="标签类型")
    parent_id: Optional[str] = Field(None, description="父标签ID")
    sort_order: int = Field(default=0, description="排序权重")


class TagResp(BaseModel):
    """标签响应"""
    id: str
    name: str
    tag_type: str
    parent_id: Optional[str] = None
    sort_order: int
    children: list["TagResp"] = []

    class Config:
        from_attributes = True


# ────────────────────────── 通用响应 ──────────────────────────

class ApiResp(BaseModel):
    """通用API响应包装"""
    code: int = 0  # 0=成功, 非0=错误码
    message: str = "ok"
    data: Optional[object] = None
