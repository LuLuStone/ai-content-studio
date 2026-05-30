"""有声书 CRUD API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audiobook import Audiobook
from app.schemas.audiobook import AudiobookOut, AudiobookListOut

router = APIRouter(prefix="/api/audiobooks", tags=["audiobooks"])


@router.get("", response_model=List[AudiobookListOut])
def list_audiobooks(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """有声书列表"""
    query = db.query(Audiobook).order_by(Audiobook.created_at.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{audiobook_id}", response_model=AudiobookOut)
def get_audiobook(audiobook_id: str, db: Session = Depends(get_db)):
    """有声书详情"""
    audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not audiobook:
        raise HTTPException(status_code=404, detail="有声书不存在")
    return audiobook


@router.delete("/{audiobook_id}")
def delete_audiobook(audiobook_id: str, db: Session = Depends(get_db)):
    """删除有声书"""
    audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not audiobook:
        raise HTTPException(status_code=404, detail="有声书不存在")
    db.delete(audiobook)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{audiobook_id}/audio")
def download_audiobook_audio(audiobook_id: str, db: Session = Depends(get_db)):
    """下载有声书音频"""
    audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not audiobook:
        raise HTTPException(status_code=404, detail="有声书不存在")
    if not audiobook.audio_file_path:
        raise HTTPException(status_code=404, detail="音频文件不存在")

    import os
    if not os.path.exists(audiobook.audio_file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")

    with open(audiobook.audio_file_path, "rb") as f:
        audio_data = f.read()

    from urllib.parse import quote
    encoded_name = quote(f"{audiobook.title}.mp3")
    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "Accept-Ranges": "bytes",
        },
    )
