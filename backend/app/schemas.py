"""
Pydantic request/response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRegisterReq(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)
    role: str = Field(default="teacher", pattern="^(teacher|student)$")
    nickname: Optional[str] = Field(None, max_length=50)
    school: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserLoginReq(BaseModel):
    username: str
    password: str


class WechatLoginReq(BaseModel):
    code: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserInfoResp(BaseModel):
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
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfoResp


class UpdateProfileReq(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    school: Optional[str] = None


class QuestionOption(BaseModel):
    label: str
    text: str


MAX_DIFFICULTY_LEVEL = 20


class QuestionCreateReq(BaseModel):
    content: str = Field(..., min_length=1)
    answer: Optional[str] = None
    analysis: Optional[str] = None
    question_type: str = Field(
        default="choice",
        pattern="^(choice|fill|experiment|calculation|short_answer)$",
    )
    difficulty: int = Field(default=3, ge=1, le=MAX_DIFFICULTY_LEVEL)
    source: Optional[str] = Field(None, max_length=200)
    options: Optional[list[dict]] = None
    tag_ids: Optional[list[str]] = None
    ocr_record_id: Optional[str] = None
    source_image_url: Optional[str] = Field(None, max_length=512)
    images: Optional[list[dict]] = None


class QuestionUpdateReq(BaseModel):
    content: Optional[str] = None
    answer: Optional[str] = None
    analysis: Optional[str] = None
    question_type: Optional[str] = Field(
        None,
        pattern="^(choice|fill|experiment|calculation|short_answer)$",
    )
    difficulty: Optional[int] = Field(None, ge=1, le=MAX_DIFFICULTY_LEVEL)
    source: Optional[str] = None
    options: Optional[list[dict]] = None
    is_public: Optional[bool] = None
    is_verified: Optional[bool] = None
    tag_ids: Optional[list[str]] = None
    source_image_url: Optional[str] = None
    images: Optional[list[dict]] = None


class QuestionResp(BaseModel):
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
    tags: list[dict] = []
    images: list[dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionListReq(BaseModel):
    keyword: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    tag_ids: Optional[str] = None
    is_public: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class QuestionListResp(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[QuestionResp]


class OcrResp(BaseModel):
    record_id: str
    origin_image_url: str
    result_latex: str
    result_text: str
    confidence: Optional[float] = None
    created_at: datetime


class OcrCorrectReq(BaseModel):
    record_id: str
    corrected_latex: str
    corrected_text: Optional[str] = None


class UserQuotaProfileUpdateReq(BaseModel):
    plan_code: str = Field(default="default", min_length=1, max_length=50)
    plan_name: Optional[str] = Field(None, max_length=100)
    daily_ocr_limit: Optional[int] = Field(None, ge=0, le=100000)
    monthly_ocr_limit: Optional[int] = Field(None, ge=0, le=1000000)
    status: str = Field(default="active", pattern="^(active|paused|expired)$")
    source: str = Field(default="manual", pattern="^(manual|seed|payment)$")
    starts_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class BillingOrderCreateReq(BaseModel):
    product_type: str = Field(default="seed_paid_lifetime", pattern="^seed_paid_lifetime$")
    channel: str = Field(default="wechat_miniapp", pattern="^(wechat_miniapp|alipay)$")


class AdminBillingGrantEntitlementReq(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=32)
    source: str = Field(default="manual_grant", pattern="^(manual_grant|seed_free|seed_paid)$")
    notes: Optional[str] = Field(None, max_length=500)


class PaperCreateManualReq(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=200)
    question_ids: list[str] = Field(..., min_length=1)
    scores: Optional[list[float]] = None
    total_score: int = 100
    exam_duration: int = 60


class PaperAutoCreateReq(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=200)
    rules: list[dict]
    tag_ids: Optional[list[str]] = None
    total_score: int = 100
    exam_duration: int = 60


class PaperResp(BaseModel):
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


class TagCreateReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    tag_type: str = Field(..., pattern="^(book|knowledge|type|difficulty)$")
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None


class TagUpdateReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    sort_order: Optional[int] = None


class TagResp(BaseModel):
    id: str
    name: str
    tag_type: str
    parent_id: Optional[str] = None
    sort_order: int
    children: list["TagResp"] = []

    class Config:
        from_attributes = True


class ApiResp(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Optional[object] = None
