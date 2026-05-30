"""自定义音色模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.database import Base


class CustomVoice(Base):
    __tablename__ = "custom_voices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, comment="音色名称")
    description = Column(String(200), nullable=True, comment="音色描述")
    sample_file_path = Column(String(500), nullable=False, comment="音频样本文件路径")
    sample_duration = Column(String(20), nullable=True, comment="样本时长")
    preview_file_path = Column(String(500), nullable=True, comment="试听音频缓存路径")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
