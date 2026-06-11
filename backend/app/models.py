"""SQLAlchemy 数据库模型定义 — 用户 / 题库 / 试卷 / 识别记录"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Enum, Float,
    ForeignKey, JSON, UniqueConstraint, Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.mysql import CHAR


class Base(DeclarativeBase):
    pass


def gen_uuid() -> str:
    return uuid.uuid4().hex


# ────────────────────────── 用户表 ──────────────────────────

class User(Base):
    __tablename__ = "user"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    phone = Column(String(20), unique=True, nullable=True, comment="手机号(微信绑定)")
    openid = Column(String(100), unique=True, nullable=True, index=True, comment="微信小程序OpenID")
    hashed_password = Column(String(256), nullable=False, comment="密码哈希")
    role = Column(
        Enum("teacher", "student", name="user_role"),
        default="teacher",
        comment="角色: teacher=老师, student=学生"
    )
    nickname = Column(String(50), nullable=True, comment="昵称/真实姓名")
    school = Column(String(100), nullable=True, comment="所属学校")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    questions = relationship("Question", back_populates="author", lazy="dynamic")
    papers = relationship("Paper", back_populates="author", lazy="dynamic")
    ocr_records = relationship("OcrRecord", back_populates="user", lazy="dynamic")


# ────────────────────────── 题目分类标签 ──────────────────────────

class QuestionTag(Base):
    __tablename__ = "question_tag"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="标签ID")
    name = Column(String(50), unique=True, nullable=False, comment="标签名")
    parent_id = Column(CHAR(32), ForeignKey("question_tag.id"), nullable=True, comment="父标签ID(树形结构)")
    tag_type = Column(
        Enum("book", "knowledge", "type", "difficulty", name="tag_type"),
        nullable=False,
        comment="book=教材册别, knowledge=知识点, type=题型, difficulty=难度"
    )
    sort_order = Column(Integer, default=0, comment="排序权重")

    children = relationship("QuestionTag", backref="parent", remote_side=[id])


# ────────────────────────── 题目表 ──────────────────────────

class Question(Base):
    __tablename__ = "question"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="题目ID")
    author_id = Column(CHAR(32), ForeignKey("user.id"), nullable=False, index=True, comment="作者ID(老师)")
    content = Column(Text, nullable=False, comment="题目正文(LaTeX格式: $H_2SO_4$ + $NaOH$ → ...)")
    answer = Column(Text, nullable=True, comment="答案(LaTeX格式)")
    analysis = Column(Text, nullable=True, comment="解析(LaTeX格式)")
    question_type = Column(
        Enum("choice", "fill", "experiment", "calculation", "short_answer", name="q_type"),
        default="choice",
        comment="题型: choice=选择题, fill=填空题, experiment=实验题, calculation=计算题, short_answer=简答题"
    )
    difficulty = Column(Integer, default=3, comment="难度: 1-5  (1=极易, 5=极难)")
    source = Column(String(200), nullable=True, comment="题目来源(如'2024年高考全国卷I')")
    source_image_url = Column(String(512), nullable=True, comment="原始拍照图片URL(仅OCR录入时有)")

    # 结构化存储(选择题)
    options = Column(JSON, nullable=True, comment="选择题选项数组: ['A. ...', 'B. ...', 'C. ...', 'D. ...']")

    # 状态
    is_public = Column(Boolean, default=False, comment="是否公开(公开题目所有老师可见)")
    is_verified = Column(Boolean, default=False, comment="是否已校对")
    ocr_record_id = Column(CHAR(32), ForeignKey("ocr_record.id"), nullable=True, comment="关联的OCR识别记录")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    author = relationship("User", back_populates="questions")
    ocr_record = relationship("OcrRecord", back_populates="question", uselist=False)
    tags = relationship("QuestionTagRel", back_populates="question", cascade="all, delete-orphan")
    images = relationship("QuestionImage", back_populates="question", cascade="all, delete-orphan")


# ────────────────────────── 题目图片 ──────────────────────────

class QuestionImage(Base):
    """题目中裁剪出的图片（电解池、有机结构式、实验装置等）"""
    __tablename__ = "question_image"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="图片ID")
    question_id = Column(CHAR(32), ForeignKey("question.id"), nullable=True, comment="关联题目")
    ocr_record_id = Column(CHAR(32), ForeignKey("ocr_record.id"), nullable=True, comment="关联OCR记录")
    image_url = Column(String(512), nullable=False, comment="图片URL(COS)")
    image_type = Column(String(50), default="figure", comment="图片类型: figure/apparatus/structure/table")
    source_bbox = Column(JSON, nullable=True, comment="在原图中的位置 [x1,y1,x2,y2]")
    width = Column(Integer, nullable=True, comment="图片宽度(px)")
    height = Column(Integer, nullable=True, comment="图片高度(px)")
    sort_order = Column(Integer, default=0, comment="在题目中的出现顺序")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    question = relationship("Question", back_populates="images")
    ocr_record = relationship("OcrRecord")


# ────────────────────────── 题目-标签关联 ──────────────────────────

class QuestionTagRel(Base):
    __tablename__ = "question_tag_rel"
    __table_args__ = (
        UniqueConstraint("question_id", "tag_id", name="uq_question_tag"),
    )

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="关联ID")
    question_id = Column(CHAR(32), ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(CHAR(32), ForeignKey("question_tag.id", ondelete="CASCADE"), nullable=False)

    question = relationship("Question", back_populates="tags")
    tag = relationship("QuestionTag")


# ────────────────────────── 试卷表 ──────────────────────────

class Paper(Base):
    __tablename__ = "paper"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="试卷ID")
    author_id = Column(CHAR(32), ForeignKey("user.id"), nullable=False, index=True, comment="创建老师ID")
    title = Column(String(200), nullable=False, comment="试卷标题")
    subtitle = Column(String(200), nullable=True, comment="副标题")

    # 组卷参数（记录生成时的筛选条件）
    filter_params = Column(JSON, nullable=True, comment="组卷筛选参数(知识点/难度/题型/数量)")

    # 试卷结构
    sections = Column(JSON, nullable=True, comment="试卷结构: [{title: '一、选择题', questions: ['id1','id2']}]")

    total_score = Column(Integer, default=100, comment="总分")
    exam_duration = Column(Integer, default=60, comment="考试时长(分钟)")

    # 导出记录
    word_url = Column(String(512), nullable=True, comment="导出的Word文件URL(COS)")
    answer_word_url = Column(String(512), nullable=True, comment="答案卷Word URL")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    author = relationship("User", back_populates="papers")
    items = relationship("PaperItem", back_populates="paper", cascade="all, delete-orphan")


# ────────────────────────── 试卷-题目明细 ──────────────────────────

class PaperItem(Base):
    __tablename__ = "paper_item"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="明细ID")
    paper_id = Column(CHAR(32), ForeignKey("paper.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(CHAR(32), ForeignKey("question.id"), nullable=False)
    sort_order = Column(Integer, default=0, comment="题目序号")
    score = Column(Float, default=5, comment="本题分值")

    paper = relationship("Paper", back_populates="items")
    question = relationship("Question")


# ────────────────────────── OCR识别记录 ──────────────────────────

class OcrRecord(Base):
    __tablename__ = "ocr_record"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="识别记录ID")
    user_id = Column(CHAR(32), ForeignKey("user.id"), nullable=False, index=True, comment="上传用户ID")
    origin_image_url = Column(String(512), nullable=False, comment="原始图片URL(COS)")
    processed_image_url = Column(String(512), nullable=True, comment="预处理后图片URL")
    ocr_result_raw = Column(Text, nullable=True, comment="OCR原始识别结果(JSON)")
    ocr_result_latex = Column(Text, nullable=True, comment="OCR结果-LaTeX格式")
    ocr_result_text = Column(Text, nullable=True, comment="OCR结果-纯文本")
    ocr_engine = Column(String(50), default="pix2text", comment="使用的OCR引擎")
    confidence = Column(Float, nullable=True, comment="识别置信度 0-1")

    # 人工修正记录
    manual_corrections = Column(JSON, nullable=True, comment="人工修正记录")

    created_at = Column(DateTime, default=datetime.now, comment="识别时间")

    # 关系
    user = relationship("User", back_populates="ocr_records")
    question = relationship("Question", back_populates="ocr_record", uselist=False)


# ────────────────────────── 错题本(学生端) ──────────────────────────

class MistakeBook(Base):
    __tablename__ = "mistake_book"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="错题记录ID")
    student_id = Column(CHAR(32), ForeignKey("user.id"), nullable=False, index=True, comment="学生ID")
    question_id = Column(CHAR(32), ForeignKey("question.id"), nullable=False, comment="题目ID")
    wrong_count = Column(Integer, default=1, comment="做错次数")
    is_mastered = Column(Boolean, default=False, comment="是否已掌握")
    last_wrong_at = Column(DateTime, default=datetime.now, comment="最近做错时间")
    notes = Column(Text, nullable=True, comment="学生笔记")
    created_at = Column(DateTime, default=datetime.now)

    student = relationship("User")
    question = relationship("Question")


# ────────────────────────── 刷题记录 ──────────────────────────

class PracticeRecord(Base):
    __tablename__ = "practice_record"

    id = Column(CHAR(32), primary_key=True, default=gen_uuid, comment="记录ID")
    student_id = Column(CHAR(32), ForeignKey("user.id"), nullable=False, index=True)
    question_id = Column(CHAR(32), ForeignKey("question.id"), nullable=False)
    student_answer = Column(Text, nullable=True, comment="学生作答内容")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")
    duration_seconds = Column(Integer, nullable=True, comment="作答耗时(秒)")
    created_at = Column(DateTime, default=datetime.now)

    student = relationship("User")
    question = relationship("Question")


# ────────────────────────── 数据库索引 ──────────────────────────
Index("ix_question_author_type", Question.author_id, Question.question_type)
Index("ix_question_difficulty", Question.difficulty)
Index("ix_ocr_user_created", OcrRecord.user_id, OcrRecord.created_at)
Index("ix_practice_student", PracticeRecord.student_id, PracticeRecord.created_at)