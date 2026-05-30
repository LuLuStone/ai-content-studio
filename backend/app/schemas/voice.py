"""自定义音色 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VoiceCreate(BaseModel):
    """创建音色"""
    name: str = Field(..., min_length=1, max_length=50, description="音色名称")
    description: Optional[str] = Field(None, max_length=200, description="音色描述")


class VoicePreview(BaseModel):
    """试听请求"""
    text: str = Field(default="你好，我是你的专属语音助手。今天天气真不错，一起出去走走吧？", max_length=500)


class VoiceOut(BaseModel):
    """音色详情"""
    id: str
    name: str
    description: Optional[str] = None
    sample_file_path: str
    sample_duration: Optional[str] = None
    preview_file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoiceListOut(BaseModel):
    """音色列表项"""
    id: str
    name: str
    description: Optional[str] = None
    sample_duration: Optional[str] = None
    preview_file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceRename(BaseModel):
    """重命名音色"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
