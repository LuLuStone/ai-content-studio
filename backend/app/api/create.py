"""统一创作入口 API"""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.schemas.create import CreateRequest, CreateResponse
from app.schemas.podcast import PodcastConfig
from app.schemas.audiobook import AudiobookConfig
from app.schemas.video import VideoConfig
from app.schemas.image import ImageConfig

router = APIRouter(prefix="/api", tags=["create"])


@router.post("/create", response_model=CreateResponse)
def create_content(req: CreateRequest, db: Session = Depends(get_db)):
    """
    统一创作入口

    根据 type 字段分发到不同的 Celery 任务：
    - podcast: 播客生成
    - audiobook: 有声书生成
    - video: 视频生成
    - image: 图片生成
    """
    # 创建任务记录
    task_id = str(uuid.uuid4())
    task = Task(
        id=task_id,
        type=req.type,
        status="pending",
        progress=0,
    )
    db.add(task)
    db.commit()

    # 分发到对应的 Celery 任务
    if req.type == "podcast":
        from app.tasks.podcast_task import generate_podcast
        generate_podcast.delay(task_id, req.input_text, req.options)

    elif req.type == "audiobook":
        from app.tasks.audiobook_task import generate_audiobook
        generate_audiobook.delay(task_id, req.input_text, req.options)

    elif req.type == "video":
        from app.tasks.video_task import generate_video
        generate_video.delay(task_id, req.input_text, req.options)

    elif req.type == "image":
        from app.tasks.image_task import generate_image
        generate_image.delay(task_id, req.input_text, req.options)

    else:
        return CreateResponse(
            task_id=task_id,
            status="failed",
            message=f"不支持的创作类型: {req.type}",
        )

    return CreateResponse(
        task_id=task_id,
        status="pending",
        message=f"创作任务已提交，请等待处理",
    )
