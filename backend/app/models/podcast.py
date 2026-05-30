"""播客模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON
from app.database import Base


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="播客标题")
    description = Column(Text, nullable=True, comment="简介")
    original_input = Column(Text, nullable=False, comment="用户原始输入")
    script_json = Column(JSON, nullable=False, comment="完整播客脚本")
    speakers_json = Column(JSON, nullable=False, comment="角色列表")
    audio_file_path = Column(String(500), nullable=True, comment="音频文件路径")
    duration_seconds = Column(Float, nullable=True, comment="时长（秒）")
    speaker_count = Column(Integer, nullable=False, comment="角色人数")
    style = Column(String(50), nullable=True, comment="播客风格")
    status = Column(String(20), nullable=False, default="completed", comment="状态")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
