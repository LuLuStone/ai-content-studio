"""统一创作入口 Schema"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CreateRequest(BaseModel):
    """创作请求"""
    input_text: Optional[str] = Field(None, description="输入文本")
    type: str = Field(..., description="创作类型：podcast/audiobook/video/image")
    options: Dict[str, Any] = Field(default_factory=dict, description="类型相关配置")


class CreateResponse(BaseModel):
    """创作响应"""
    task_id: str
    status: str
    message: str
