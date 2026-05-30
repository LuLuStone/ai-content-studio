"""音频处理工具"""

import io
import os
from pydub import AudioSegment


def merge_audio_segments(audio_segments: list[tuple[str, bytes]], gap_ms: int = 800) -> bytes:
    """
    将多段音频拼接成一个完整文件

    Args:
        audio_segments: [(label, audio_bytes), ...]
        gap_ms: 段落间静音时长（毫秒）

    Returns:
        MP3 格式的音频字节数据
    """
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=gap_ms)

    for i, (label, audio_bytes) in enumerate(audio_segments):
        segment = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        if i > 0:
            combined += silence
        combined += segment

    # 导出为 MP3
    output = io.BytesIO()
    combined.export(output, format="mp3", bitrate="192k")
    return output.getvalue()


def get_audio_duration(audio_bytes: bytes, format: str = "mp3") -> float:
    """获取音频时长（秒）"""
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=format)
    return len(audio) / 1000.0


def save_audio(audio_bytes: bytes, file_path: str) -> str:
    """保存音频文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    return file_path
