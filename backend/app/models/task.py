"""任务模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(20), nullable=False, comment="podcast/audiobook/video/image")
    status = Column(String(20), nullable=False, default="pending", comment="pending/processing/completed/failed")
    progress = Column(Integer, default=0, comment="进度百分比 0-100")
    result_id = Column(String(36), nullable=True, comment="关联的结果 ID")
    error_message = Column(Text, nullable=True, comment="失败原因")
    step_data = Column(JSON, nullable=True, comment="各阶段中间数据")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
