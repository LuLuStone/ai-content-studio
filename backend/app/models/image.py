"""图片模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="标题")
    original_input = Column(Text, nullable=False, comment="用户原始描述")
    prompt_cn = Column(Text, nullable=True, comment="中文描述")
    prompt_en = Column(Text, nullable=True, comment="英文生成 Prompt")
    image_file_path = Column(String(500), nullable=True, comment="图片文件路径")
    style = Column(String(50), nullable=True, comment="图片风格")
    aspect_ratio = Column(String(10), nullable=True, comment="宽高比")
    status = Column(String(20), nullable=False, default="completed", comment="状态")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
