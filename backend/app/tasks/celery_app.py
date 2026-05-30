"""Celery 配置"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_content_studio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 单个任务最大执行时间 10 分钟
    worker_max_tasks_per_child=100,
    broker_connection_retry_on_startup=True,
)

# 显式导入任务模块（确保 Celery 能发现任务）
import app.tasks.podcast_task  # noqa
import app.tasks.audiobook_task  # noqa
import app.tasks.video_task  # noqa
import app.tasks.image_task  # noqa
