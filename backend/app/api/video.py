"""视频 CRUD API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.schemas.video import VideoOut, VideoListOut

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("", response_model=List[VideoListOut])
def list_videos(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """视频列表"""
    query = db.query(Video).order_by(Video.created_at.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{video_id}", response_model=VideoOut)
def get_video(video_id: str, db: Session = Depends(get_db)):
    """视频详情"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return video


@router.delete("/{video_id}")
def delete_video(video_id: str, db: Session = Depends(get_db)):
    """删除视频"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    db.delete(video)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{video_id}/video")
def download_video(video_id: str, db: Session = Depends(get_db)):
    """下载视频"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    if not video.video_file_path:
        raise HTTPException(status_code=404, detail="视频文件不存在")

    import os
    if not os.path.exists(video.video_file_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")

    with open(video.video_file_path, "rb") as f:
        video_data = f.read()

    return Response(
        content=video_data,
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{video.title}.mp4"'},
    )
