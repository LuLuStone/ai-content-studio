"""图片 CRUD API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.image import Image
from app.schemas.image import ImageOut, ImageListOut

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("", response_model=List[ImageListOut])
def list_images(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """图片列表"""
    query = db.query(Image).order_by(Image.created_at.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{image_id}", response_model=ImageOut)
def get_image(image_id: str, db: Session = Depends(get_db)):
    """图片详情"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    return image


@router.delete("/{image_id}")
def delete_image(image_id: str, db: Session = Depends(get_db)):
    """删除图片"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    db.delete(image)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{image_id}/file")
def get_image_file(image_id: str, db: Session = Depends(get_db)):
    """获取图片文件"""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="图片不存在")
    if not image.image_file_path:
        raise HTTPException(status_code=404, detail="图片文件不存在")

    import os
    if not os.path.exists(image.image_file_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")

    # 根据扩展名判断 media type
    ext = os.path.splitext(image.image_file_path)[1].lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    with open(image.image_file_path, "rb") as f:
        image_data = f.read()

    return Response(
        content=image_data,
        media_type=media_type,
    )
