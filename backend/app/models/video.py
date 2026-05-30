"""视频模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, JSON
from app.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="标题")
    original_input = Column(Text, nullable=False, comment="原始输入")
    script_json = Column(JSON, nullable=True, comment="分镜脚本")
    video_file_path = Column(String(500), nullable=True, comment="视频文件路径")
    thumbnail_path = Column(String(500), nullable=True, comment="缩略图路径")
    duration_seconds = Column(Float, nullable=True, comment="时长")
    style = Column(String(50), nullable=True, comment="视频风格")
    status = Column(String(20), nullable=False, default="completed", comment="状态")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
