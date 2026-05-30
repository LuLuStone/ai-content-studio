"""自定义音色 CRUD API"""

import os
import uuid
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.voice import CustomVoice
from app.schemas.voice import VoiceOut, VoiceListOut, VoiceRename
from app.services.tts_service import tts_service, VOICE_OPTIONS
from app.config import get_settings

router = APIRouter(prefix="/api/voices", tags=["voices"])

settings = get_settings()

# 允许的音频格式
ALLOWED_EXTENSIONS = {".mp3", ".wav"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 预置音色试听缓存目录
PRESET_CACHE_DIR = "voices/presets"


def _get_preset_cache_path(voice_id: str) -> str:
    return os.path.join(settings.STORAGE_PATH, PRESET_CACHE_DIR, f"{voice_id}.wav")


# ===== 预置音色 =====

@router.get("/presets")
def list_preset_voices():
    """获取系统预置音色列表"""
    presets = []
    for vid, info in VOICE_OPTIONS.items():
        cache_path = _get_preset_cache_path(vid)
        presets.append({
            "id": vid,
            "name": vid,
            "description": info["desc"],
            "gender": info["gender"],
            "lang": info["lang"],
            "has_preview": os.path.exists(cache_path),
        })
    return presets


@router.post("/presets/{voice_id}/preview")
def preview_preset_voice(voice_id: str, force: bool = False):
    """试听预置音色（带缓存）"""
    if voice_id not in VOICE_OPTIONS:
        raise HTTPException(status_code=404, detail="预置音色不存在")

    cache_path = _get_preset_cache_path(voice_id)

    # 检查缓存
    if not force and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return Response(content=f.read(), media_type="audio/wav")

    # 调 API 生成
    test_text = "你好，我是你的语音助手。今天天气真不错，一起出去走走吧？"
    try:
        audio_bytes = tts_service.synthesize(text=test_text, voice_id=voice_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")

    # 保存缓存
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "wb") as f:
        f.write(audio_bytes)

    return Response(content=audio_bytes, media_type="audio/wav")


@router.get("/presets/{voice_id}/audio")
def get_preset_audio(voice_id: str):
    """获取预置音色的缓存试听音频"""
    if voice_id not in VOICE_OPTIONS:
        raise HTTPException(status_code=404, detail="预置音色不存在")

    cache_path = _get_preset_cache_path(voice_id)
    if not os.path.exists(cache_path):
        raise HTTPException(status_code=404, detail="暂无试听，请先点击试听生成")

    with open(cache_path, "rb") as f:
        return Response(content=f.read(), media_type="audio/wav")


# ===== 自定义音色 =====

@router.get("", response_model=List[VoiceListOut])
def list_voices(db: Session = Depends(get_db)):
    """获取自定义音色列表"""
    voices = db.query(CustomVoice).order_by(CustomVoice.created_at.desc()).all()
    return voices


@router.post("", response_model=VoiceOut)
async def create_voice(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传音频样本，创建自定义音色"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 mp3 和 wav 格式")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="音频文件不能超过 10MB")

    voice_id = str(uuid.uuid4())
    storage_dir = os.path.join(settings.STORAGE_PATH, "voices")
    os.makedirs(storage_dir, exist_ok=True)
    filename = f"{voice_id}{ext}"
    file_path = os.path.join(storage_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    relative_path = f"voices/{filename}"
    voice = CustomVoice(
        id=voice_id,
        name=name,
        description=description or None,
        sample_file_path=relative_path,
    )
    db.add(voice)
    db.commit()
    db.refresh(voice)

    return voice


@router.get("/{voice_id}", response_model=VoiceOut)
def get_voice(voice_id: str, db: Session = Depends(get_db)):
    """获取音色详情"""
    voice = db.query(CustomVoice).filter(CustomVoice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="音色不存在")
    return voice


@router.patch("/{voice_id}", response_model=VoiceOut)
def rename_voice(voice_id: str, body: VoiceRename, db: Session = Depends(get_db)):
    """重命名自定义音色"""
    voice = db.query(CustomVoice).filter(CustomVoice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="音色不存在")

    if body.name is not None:
        voice.name = body.name
    if body.description is not None:
        voice.description = body.description

    db.commit()
    db.refresh(voice)
    return voice


@router.get("/{voice_id}/sample")
def get_voice_sample(voice_id: str, db: Session = Depends(get_db)):
    """获取音频样本文件"""
    voice = db.query(CustomVoice).filter(CustomVoice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="音色不存在")

    file_path = os.path.join(settings.STORAGE_PATH, voice.sample_file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")

    with open(file_path, "rb") as f:
        content = f.read()

    media_type = "audio/mpeg" if file_path.endswith(".mp3") else "audio/wav"
    return Response(content=content, media_type=media_type)


@router.post("/{voice_id}/preview")
def preview_voice(voice_id: str, force: bool = False, db: Session = Depends(get_db)):
    """试听自定义音色（带缓存）"""
    voice = db.query(CustomVoice).filter(CustomVoice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="音色不存在")

    # 检查缓存
    if not force and voice.preview_file_path:
        cached_path = os.path.join(settings.STORAGE_PATH, voice.preview_file_path)
        if os.path.exists(cached_path):
            with open(cached_path, "rb") as f:
                return Response(content=f.read(), media_type="audio/wav")

    # 调 API 生成
    sample_path = os.path.join(settings.STORAGE_PATH, voice.sample_file_path)
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="音频样本文件不存在")

    with open(sample_path, "rb") as f:
        sample_bytes = f.read()

    test_text = "你好，我是你的专属语音助手。今天天气真不错，一起出去走走吧？"
    try:
        audio_bytes = tts_service.synthesize_with_clone(
            text=test_text,
            sample_audio_bytes=sample_bytes,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")

    # 保存缓存
    preview_dir = os.path.join(settings.STORAGE_PATH, "voices", "previews")
    os.makedirs(preview_dir, exist_ok=True)
    preview_filename = f"{voice_id}_preview.wav"
    preview_path = os.path.join(preview_dir, preview_filename)
    with open(preview_path, "wb") as f:
        f.write(audio_bytes)

    voice.preview_file_path = f"voices/previews/{preview_filename}"
    db.commit()

    return Response(content=audio_bytes, media_type="audio/wav")


@router.delete("/{voice_id}")
def delete_voice(voice_id: str, db: Session = Depends(get_db)):
    """删除自定义音色"""
    voice = db.query(CustomVoice).filter(CustomVoice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="音色不存在")

    # 删除样本文件
    sample_path = os.path.join(settings.STORAGE_PATH, voice.sample_file_path)
    if os.path.exists(sample_path):
        os.remove(sample_path)

    # 删除预览缓存文件
    if voice.preview_file_path:
        preview_path = os.path.join(settings.STORAGE_PATH, voice.preview_file_path)
        if os.path.exists(preview_path):
            os.remove(preview_path)

    db.delete(voice)
    db.commit()

    return {"message": "删除成功"}
