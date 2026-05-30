"""图片生成 Celery 任务"""

import logging
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.task import Task
from app.models.image import Image
from app.services.llm_service import llm_service
from app.prompts.image_prompt import IMAGE_PROMPT_OPTIMIZE
from app.schemas.image import ImagePrompt, ImageConfig

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_image(self, task_id: str, input_text: str, options: dict):
    """
    图片生成任务

    流程：
    1. LLM 优化图像 Prompt
    2. 调用图像生成 API（待对接）
    3. 保存到数据库

    TODO: 对接火山引擎图像生成 API
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "processing"
        task.progress = 10
        db.commit()

        config = ImageConfig(**options)

        # ① LLM 优化 Prompt
        prompt = IMAGE_PROMPT_OPTIMIZE.format(
            user_input=input_text,
            style=config.style,
            aspect_ratio=config.aspect_ratio,
        )

        task.progress = 30
        db.commit()

        image_prompt = llm_service.generate_structured(prompt, ImagePrompt)

        task.progress = 50
        db.commit()

        # ② 调用图像生成 API
        # TODO: 实现图像生成对接（火山引擎或其他）
        # image_file_path = await image_service.generate(image_prompt.prompt_en)
        logger.warning("图像生成 API 尚未对接，仅保存 Prompt")

        task.progress = 80
        db.commit()

        # ③ 保存到数据库（暂时只保存 Prompt）
        image = Image(
            title=image_prompt.title,
            original_input=input_text,
            prompt_cn=image_prompt.description_cn,
            prompt_en=image_prompt.prompt_en,
            image_file_path=None,  # 待图像生成完成后更新
            style=config.style,
            aspect_ratio=config.aspect_ratio,
            status="completed",
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        task.status = "completed"
        task.progress = 100
        task.result_id = image.id
        db.commit()

        logger.info(f"图像 Prompt 生成完成: {image.id}")

    except Exception as e:
        logger.error(f"图片生成失败: {e}", exc_info=True)
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
