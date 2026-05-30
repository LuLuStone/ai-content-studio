"""视频相关 Schema"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VideoScene(BaseModel):
    scene_number: int
    duration: float = Field(..., ge=1, le=30)
    visual_description: str = Field(..., max_length=1000)
    narration: str = Field(..., max_length=500)
    subtitle: str = Field(..., max_length=100)
    transition: str = Field(default="cut", pattern="^(fade|cut|dissolve|slide)$")


class VideoScript(BaseModel):
    """LLM 生成的视频脚本结构"""
    title: str
    style: str
    total_duration: float
    scenes: List[VideoScene] = Field(..., min_items=1, max_items=20)


class VideoConfig(BaseModel):
    """视频生成配置"""
    style: str = Field(default="科技感")
    duration: int = Field(default=30, ge=5, le=120, description="目标时长（秒）")


class VideoOut(BaseModel):
    id: str
    title: str
    original_input: str
    script_json: Optional[dict] = None
    video_file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    style: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoListOut(BaseModel):
    id: str
    title: str
    duration_seconds: Optional[float] = None
    style: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
