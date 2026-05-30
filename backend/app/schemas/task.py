"""任务相关 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    type: str  # podcast / audiobook / video / image


class TaskStatus(BaseModel):
    task_id: str
    type: str
    status: str  # pending / processing / completed / failed
    progress: int = 0
    message: Optional[str] = None
    result_id: Optional[str] = None
    error_message: Optional[str] = None
    step_data: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
