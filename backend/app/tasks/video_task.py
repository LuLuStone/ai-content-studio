"""视频生成 Celery 任务"""

import logging
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.task import Task
from app.models.video import Video
from app.services.llm_service import llm_service
from app.prompts.video_storyboard import VIDEO_STORYBOARD_PROMPT
from app.schemas.video import VideoScript, VideoConfig

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_video(self, task_id: str, input_text: str, options: dict):
    """
    视频生成任务

    流程：
    1. LLM 生成分镜脚本
    2. 调用火山引擎视频生成 API（待对接）
    3. 保存到数据库

    TODO: 对接火山引擎视频生成 API
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "processing"
        task.progress = 10
        db.commit()

        config = VideoConfig(**options)

        # ① LLM 生成分镜脚本
        prompt = VIDEO_STORYBOARD_PROMPT.format(
            user_input=input_text,
            style=config.style,
            duration=config.duration,
        )

        task.progress = 30
        db.commit()

        script = llm_service.generate_structured(prompt, VideoScript)

        task.progress = 50
        db.commit()

        # ② 调用火山引擎视频生成 API
        # TODO: 实现火山引擎视频生成对接
        # video_file_path = await volcano_service.generate(script)
        logger.warning("视频生成 API 尚未对接，仅保存脚本")

        task.progress = 80
        db.commit()

        # ③ 保存到数据库（暂时只保存脚本）
        video = Video(
            title=script.title,
            original_input=input_text,
            script_json=script.model_dump(),
            video_file_path=None,  # 待视频生成完成后更新
            duration_seconds=script.total_duration,
            style=config.style,
            status="completed",
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        task.status = "completed"
        task.progress = 100
        task.result_id = video.id
        db.commit()

        logger.info(f"视频脚本生成完成: {video.id}")

    except Exception as e:
        logger.error(f"视频生成失败: {e}", exc_info=True)
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
