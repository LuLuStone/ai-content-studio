"""播客生成 Celery 任务"""

import os
import logging
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.task import Task
from app.models.podcast import Podcast
from app.services.llm_service import llm_service
from app.services.tts_service import tts_service
from app.prompts.podcast_script import PODCAST_SCRIPT_PROMPT, DEFAULT_SPEAKER_CONFIGS
from app.schemas.podcast import PodcastScript, PodcastConfig
from app.utils.audio import merge_audio_segments, get_audio_duration, save_audio
from app.utils.file import get_storage_path, generate_filename
from app.models.voice import CustomVoice
from app.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_podcast(self, task_id: str, input_text: str, options: dict):
    """播客生成任务"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = "processing"
        task.progress = 10
        task.step_data = {"stage": "generating_script"}
        db.commit()

        config = PodcastConfig(**options)
        speaker_count = config.speaker_count

        # 构造角色要求
        if config.voices:
            speaker_requirements = "用户指定的角色音色：\n"
            for role, voice in config.voices.items():
                speaker_requirements += f"- {role}: {voice}\n"
        else:
            default_speakers = DEFAULT_SPEAKER_CONFIGS.get(speaker_count, DEFAULT_SPEAKER_CONFIGS[2])
            speaker_requirements = "使用默认角色配置：\n"
            for s in default_speakers:
                speaker_requirements += f"- {s['name']}（{s['role']}）: {s['voice_id']}\n"

        # ① LLM 生成播客脚本
        prompt = PODCAST_SCRIPT_PROMPT.format(
            user_input=input_text,
            speaker_count=speaker_count,
            speaker_requirements=speaker_requirements,
            style=config.style,
            min_turns=max(speaker_count * 3, 6),
            max_turns=speaker_count * 15,
        )

        task.progress = 20
        db.commit()

        script = llm_service.generate_structured(prompt, PodcastScript)

        # 脚本生成完成，写入 step_data
        script_data = script.model_dump()
        # 把 emotion enum 转成 string
        for line in script_data.get("script", []):
            if hasattr(line.get("emotion"), "value"):
                line["emotion"] = line["emotion"].value
        for sp in script_data.get("speakers", []):
            pass  # 已经是 string

        task.progress = 40
        task.step_data = {
            "stage": "script_ready",
            "script": script_data,
            "audio_status": {str(i): "pending" for i in range(len(script.script))},
        }
        db.commit()

        # ② 并发 TTS 合成
        from concurrent.futures import ThreadPoolExecutor, as_completed

        total_lines = len(script.script)
        audio_results = [None] * total_lines

        # 预加载自定义音色样本
        settings = get_settings()
        custom_voice_samples = {}
        for voice_id in config.voices.values():
            if voice_id.startswith("custom:"):
                cv_id = voice_id.split(":", 1)[1]
                cv = db.query(CustomVoice).filter(CustomVoice.id == cv_id).first()
                if cv:
                    sample_path = os.path.join(settings.STORAGE_PATH, cv.sample_file_path)
                    if os.path.exists(sample_path):
                        with open(sample_path, "rb") as f:
                            custom_voice_samples[cv_id] = f.read()

        def synthesize_one(idx: int, line):
            voice_id = next(
                (s.voice_id for s in script.speakers if s.name == line.speaker),
                "冰糖"
            )
            emotion = line.emotion.value if hasattr(line.emotion, 'value') else line.emotion

            if voice_id.startswith("custom:"):
                cv_id = voice_id.split(":", 1)[1]
                sample_bytes = custom_voice_samples.get(cv_id)
                if sample_bytes:
                    audio_bytes = tts_service.synthesize_with_clone(
                        text=line.text,
                        sample_audio_bytes=sample_bytes,
                        emotion=emotion,
                    )
                else:
                    audio_bytes = tts_service.synthesize(text=line.text, voice_id="冰糖", emotion=emotion)
            else:
                audio_bytes = tts_service.synthesize(
                    text=line.text,
                    voice_id=voice_id,
                    emotion=emotion,
                )
            return idx, line.speaker, audio_bytes

        completed_count = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(synthesize_one, i, line)
                for i, line in enumerate(script.script)
            ]
            for future in as_completed(futures):
                idx, speaker, audio_bytes = future.result()
                audio_results[idx] = (speaker, audio_bytes)
                completed_count += 1
                progress = 40 + int(completed_count / total_lines * 40)
                task.progress = progress
                # 更新每句音频状态
                if task.step_data and "audio_status" in task.step_data:
                    task.step_data["audio_status"][str(idx)] = "done"
                    task.step_data["stage"] = "synthesizing_audio"
                db.commit()

        audio_segments = audio_results

        # ③ 音频拼接
        task.step_data["stage"] = "merging"
        db.commit()

        merged_audio = merge_audio_segments(audio_segments, gap_ms=800)

        task.progress = 90
        db.commit()

        # ④ 保存文件
        audio_dir = get_storage_path("audio")
        filename = generate_filename("mp3")
        file_path = f"{audio_dir}/{filename}"
        save_audio(merged_audio, file_path)

        # ⑤ 保存到数据库
        duration = get_audio_duration(merged_audio, "mp3")

        podcast = Podcast(
            title=script.title,
            description=script.description,
            original_input=input_text,
            script_json=script.model_dump(),
            speakers_json=[s.model_dump() for s in script.speakers],
            audio_file_path=file_path,
            duration_seconds=duration,
            speaker_count=speaker_count,
            style=config.style,
            status="completed",
        )
        db.add(podcast)
        db.commit()
        db.refresh(podcast)

        task.status = "completed"
        task.progress = 100
        task.result_id = podcast.id
        task.step_data["stage"] = "done"
        db.commit()

        logger.info(f"播客生成完成: {podcast.id}")

    except Exception as e:
        logger.error(f"播客生成失败: {e}", exc_info=True)
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    finally:
        db.close()
