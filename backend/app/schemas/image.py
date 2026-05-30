"""图片相关 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ImagePrompt(BaseModel):
    """LLM 优化后的图像 Prompt"""
    title: str
    description_cn: str
    prompt_en: str
    negative_prompt: str = ""
    style: str = "写实"
    aspect_ratio: str = "16:9"


class ImageConfig(BaseModel):
    """图片生成配置"""
    style: str = Field(default="写实", description="图片风格")
    aspect_ratio: str = Field(default="16:9", pattern="^(1:1|4:3|16:9|9:16|3:4)$")


class ImageOut(BaseModel):
    id: str
    title: str
    original_input: str
    prompt_cn: Optional[str] = None
    prompt_en: Optional[str] = None
    image_file_path: Optional[str] = None
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImageListOut(BaseModel):
    id: str
    title: str
    image_file_path: Optional[str] = None
    style: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
