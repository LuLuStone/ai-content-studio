"""播客 CRUD API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.podcast import Podcast
from app.schemas.podcast import PodcastOut, PodcastListOut

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])


@router.get("", response_model=List[PodcastListOut])
def list_podcasts(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """播客列表"""
    query = db.query(Podcast).order_by(Podcast.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{podcast_id}", response_model=PodcastOut)
def get_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """播客详情"""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="播客不存在")
    return podcast


@router.delete("/{podcast_id}")
def delete_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """删除播客"""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="播客不存在")
    db.delete(podcast)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{podcast_id}/audio")
def download_podcast_audio(podcast_id: str, db: Session = Depends(get_db)):
    """下载播客音频"""
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if not podcast:
        raise HTTPException(status_code=404, detail="播客不存在")
    if not podcast.audio_file_path:
        raise HTTPException(status_code=404, detail="音频文件不存在")

    import os
    if not os.path.exists(podcast.audio_file_path):
        raise HTTPException(status_code=404, detail="音频文件不存在")

    with open(podcast.audio_file_path, "rb") as f:
        audio_data = f.read()

    from urllib.parse import quote
    encoded_name = quote(f"{podcast.title}.mp3")
    return Response(
        content=audio_data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "Accept-Ranges": "bytes",
        },
    )
