"""有声书相关 Schema"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.podcast import PodcastEmotion


class AudiobookCharacter(BaseModel):
    name: str
    gender: str = Field(..., pattern="^(male|female)$")
    age_group: str = Field(..., pattern="^(少年|青年|中年|老年)$")
    voice_id: str
    voice_description: str = Field(default="", description="音色描述，用于音色设计模型")


class AudiobookSegment(BaseModel):
    character: str
    text: str = Field(..., min_length=1, max_length=2000)
    emotion: PodcastEmotion


class AudiobookScript(BaseModel):
    """LLM 生成的有声书脚本结构"""
    title: str
    characters: List[AudiobookCharacter] = Field(..., min_items=1)
    segments: List[AudiobookSegment] = Field(..., min_items=1)


class AudiobookConfig(BaseModel):
    """有声书生成配置"""
    mode: str = Field(default="single", pattern="^(single|multi)$")
    voice_id: str = Field(default="冰糖", description="单模式时的音色")
    speed: str = Field(default="normal", pattern="^(slow|normal|fast)$")
    style: str = Field(default="自然", description="朗读风格")


class AudiobookOut(BaseModel):
    id: str
    title: str
    original_input: str
    script_json: Optional[dict] = None
    characters_json: Optional[list] = None
    audio_file_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    mode: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AudiobookListOut(BaseModel):
    id: str
    title: str
    duration_seconds: Optional[float] = None
    mode: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
