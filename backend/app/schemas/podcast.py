"""播客相关 Schema"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PodcastEmotion(str, Enum):
    neutral = "neutral"
    happy = "happy"
    excited = "excited"
    serious = "serious"
    surprised = "surprised"
    thoughtful = "thoughtful"
    sad = "sad"
    angry = "angry"
    curious = "curious"
    lively = "lively"
    narrative = "narrative"
    calm = "calm"
    warm = "warm"
    humorous = "humorous"
    anxious = "anxious"
    nostalgic = "nostalgic"
    proud = "proud"
    worried = "worried"
    confident = "confident"


class PodcastSpeaker(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    role: str = Field(..., description="主持人/嘉宾/专家等")
    voice_id: str = Field(..., description="TTS 音色 ID")


class PodcastLine(BaseModel):
    speaker: str
    role: str
    text: str = Field(..., min_length=1, max_length=1000)
    emotion: PodcastEmotion


class PodcastScript(BaseModel):
    """LLM 生成的播客脚本结构"""
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    speakers: List[PodcastSpeaker] = Field(..., min_items=2, max_items=4)
    script: List[PodcastLine] = Field(..., min_items=4, max_items=100)


class PodcastConfig(BaseModel):
    """播客生成配置"""
    speaker_count: int = Field(default=2, ge=2, le=4)
    style: str = Field(default="轻松闲聊")
    voices: dict = Field(default_factory=dict, description="角色音色映射")


class PodcastOut(BaseModel):
    """播客详情响应"""
    id: str
    title: str
    description: Optional[str] = None
    original_input: str
    script_json: dict
    speakers_json: list
    audio_file_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    speaker_count: int
    style: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PodcastListOut(BaseModel):
    """播客列表项"""
    id: str
    title: str
    description: Optional[str] = None
    duration_seconds: Optional[float] = None
    speaker_count: int
    style: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
