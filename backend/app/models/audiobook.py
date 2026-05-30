"""有声书模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, JSON
from app.database import Base


class Audiobook(Base):
    __tablename__ = "audiobooks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, comment="标题")
    original_input = Column(Text, nullable=False, comment="原始文本")
    script_json = Column(JSON, nullable=True, comment="角色标注脚本")
    characters_json = Column(JSON, nullable=True, comment="角色音色映射")
    audio_file_path = Column(String(500), nullable=True, comment="音频文件路径")
    duration_seconds = Column(Float, nullable=True, comment="时长")
    mode = Column(String(20), nullable=False, default="single", comment="single/multi")
    status = Column(String(20), nullable=False, default="completed", comment="状态")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
