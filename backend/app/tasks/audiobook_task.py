"""有声书生成 Celery 任务"""

import os
import logging
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.task import Task
from app.models.audiobook import Audiobook
from app.services.llm_service import llm_service
from app.services.tts_service import tts_service
from app.prompts.audiobook_script import AUDIOBOOK_MULTI_PROMPT, AUDIOBOOK_SINGLE_PROMPT
from app.schemas.audiobook import AudiobookScript, AudiobookConfig
from app.utils.audio import merge_audio_segments, get_audio_duration, save_audio
from app.utils.file import get_storage_path, generate_filename
from app.models.voice import CustomVoice
from app.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_audiobook(self, task_id: str, input_text: str, options: dict):
    """有声书生成任务"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "processing"
        task.progress = 10
        task.step_data = {"stage": "generating_script"}
        db.commit()

        config = AudiobookConfig(**options)

        # ① LLM 生成朗读脚本
        if config.mode == "multi":
            prompt = AUDIOBOOK_MULTI_PROMPT.format(
                user_input=input_text,
                style=config.style,
            )
        else:
            prompt = AUDIOBOOK_SINGLE_PROMPT.format(
                user_input=input_text,
                style=config.style,
                voice_id=config.voice_id,
            )

        task.progress = 20
        db.commit()

        script = llm_service.generate_structured(prompt, AudiobookScript)

        # 脚本生成完成，写入 step_data
        script_data = script.model_dump()
        for seg in script_data.get("segments", []):
            if hasattr(seg.get("emotion"), "value"):
                seg["emotion"] = seg["emotion"].value

        task.progress = 40
        task.step_data = {
            "stage": "script_ready",
            "script": script_data,
            "audio_status": {str(i): "pending" for i in range(len(script.segments))},
        }
        db.commit()

        # 预加载自定义音色样本
        app_settings = get_settings()
        custom_sample_bytes = None
        if config.voice_id and config.voice_id.startswith("custom:"):
            cv_id = config.voice_id.split(":", 1)[1]
            cv = db.query(CustomVoice).filter(CustomVoice.id == cv_id).first()
            if cv:
                sample_path = os.path.join(app_settings.STORAGE_PATH, cv.sample_file_path)
                if os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        custom_sample_bytes = f.read()

        # ② 并发 TTS 合成
        from concurrent.futures import ThreadPoolExecutor, as_completed

        total_segments = len(script.segments)
        audio_results = [None] * total_segments

        def synthesize_one(idx: int, seg):
            character = next(
                (c for c in script.characters if c.name == seg.character),
                None
            )
            emotion = seg.emotion.value if hasattr(seg.emotion, 'value') else seg.emotion

            if config.mode == "multi" and character and character.voice_id == "voice_design":
                voice_desc = character.voice_description or f"一个{character.age_group}的{('男性' if character.gender == 'male' else '女性')}，声音自然"
                audio_bytes = tts_service.synthesize_with_voice_design(
                    text=seg.text,
                    voice_description=voice_desc,
                    emotion=emotion,
                )
            elif config.voice_id and config.voice_id.startswith("custom:") and custom_sample_bytes:
                audio_bytes = tts_service.synthesize_with_clone(
                    text=seg.text,
                    sample_audio_bytes=custom_sample_bytes,
                    emotion=emotion,
                )
            else:
                voice_id = character.voice_id if character and character.voice_id != "voice_design" else config.voice_id
                audio_bytes = tts_service.synthesize(
                    text=seg.text,
                    voice_id=voice_id,
                    emotion=emotion,
                )
            return idx, seg.character, audio_bytes

        completed_count = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(synthesize_one, i, seg)
                for i, seg in enumerate(script.segments)
            ]
            for future in as_completed(futures):
                idx, character, audio_bytes = future.result()
                audio_results[idx] = (character, audio_bytes)
                completed_count += 1
                progress = 40 + int(completed_count / total_segments * 40)
                task.progress = progress
                if task.step_data and "audio_status" in task.step_data:
                    task.step_data["audio_status"][str(idx)] = "done"
                    task.step_data["stage"] = "synthesizing_audio"
                db.commit()

        audio_segments = audio_results

        # ③ 音频拼接
        task.step_data["stage"] = "merging"
        db.commit()

        merged_audio = merge_audio_segments(audio_segments, gap_ms=600)

        task.progress = 90
        db.commit()

        # ④ 保存文件
        audio_dir = get_storage_path("audio")
        filename = generate_filename("mp3")
        file_path = f"{audio_dir}/{filename}"
        save_audio(merged_audio, file_path)

        # ⑤ 保存到数据库
        duration = get_audio_duration(merged_audio, "mp3")

        audiobook = Audiobook(
            title=script.title,
            original_input=input_text,
            script_json=script.model_dump(),
            characters_json=[c.model_dump() for c in script.characters],
            audio_file_path=file_path,
            duration_seconds=duration,
            mode=config.mode,
            status="completed",
        )
        db.add(audiobook)
        db.commit()
        db.refresh(audiobook)

        task.status = "completed"
        task.progress = 100
        task.result_id = audiobook.id
        task.step_data["stage"] = "done"
        db.commit()

        logger.info(f"有声书生成完成: {audiobook.id}")

    except Exception as e:
        logger.error(f"有声书生成失败: {e}", exc_info=True)
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
