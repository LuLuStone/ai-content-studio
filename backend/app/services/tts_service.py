"""小米 MiMo TTS 语音合成服务封装"""

import base64
import logging
from openai import OpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)

# 预置音色列表（mimo-v2.5-tts 使用）
VOICE_OPTIONS = {
    "冰糖": {"voice_id": "冰糖", "gender": "female", "lang": "zh", "desc": "女声，温柔甜美"},
    "茉莉": {"voice_id": "茉莉", "gender": "female", "lang": "zh", "desc": "女声，成熟稳重"},
    "苏打": {"voice_id": "苏打", "gender": "male", "lang": "zh", "desc": "男声，年轻活力"},
    "白桦": {"voice_id": "白桦", "gender": "male", "lang": "zh", "desc": "男声，沉稳磁性"},
    "Mia": {"voice_id": "Mia", "gender": "female", "lang": "en", "desc": "Female, English"},
    "Chloe": {"voice_id": "Chloe", "gender": "female", "lang": "en", "desc": "Female, English"},
    "Milo": {"voice_id": "Milo", "gender": "male", "lang": "en", "desc": "Male, English"},
    "Dean": {"voice_id": "Dean", "gender": "male", "lang": "en", "desc": "Male, English"},
}

# 情绪 → 风格指令映射
EMOTION_TO_STYLE = {
    "neutral": "用自然平稳的语调朗读",
    "happy": "用轻快愉悦的语调朗读，带着微笑的感觉",
    "excited": "用兴奋激动的语调朗读，语速稍快，声音明亮",
    "serious": "用严肃认真的语调朗读，语气沉稳",
    "surprised": "用惊讶的语气朗读，语调上扬",
    "thoughtful": "用沉思的语调朗读，语速稍慢，带有思考感",
    "sad": "用低沉伤感的语调朗读，语速较慢",
    "angry": "用愤怒的语调朗读，语气强硬",
    "curious": "用好奇的语调朗读，语调微微上扬，带有探索感",
    "lively": "用活泼生动的语调朗读，节奏轻快",
    "narrative": "用叙事的语调朗读，像讲故事一样",
    "calm": "用平静舒缓的语调朗读",
    "warm": "用温暖亲切的语调朗读",
    "humorous": "用幽默风趣的语调朗读，带点俏皮",
    "anxious": "用焦虑不安的语调朗读，语速稍快",
    "nostalgic": "用怀旧感伤的语调朗读，语速稍慢",
    "proud": "用自豪骄傲的语调朗读",
    "worried": "用担忧的语调朗读",
    "confident": "用自信坚定的语调朗读",
}


class TTSService:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.MIMO_API_KEY,
            base_url=settings.MIMO_BASE_URL,
        )
        self.preset_model = "mimo-v2.5-tts"          # 预置音色模型
        self.design_model = "mimo-v2.5-tts-voicedesign"  # 音色设计模型
        self.clone_model = "mimo-v2.5-tts-voiceclone"    # 音色复刻模型

    def synthesize(
        self,
        text: str,
        voice_id: str = "冰糖",
        emotion: str = "neutral",
        style_instruction: str = "",
    ) -> bytes:
        """
        使用预置音色合成语音（单人模式）

        Args:
            text: 要合成的文字
            voice_id: 预置音色 ID
            emotion: 情绪标记
            style_instruction: 自定义风格指令

        Returns:
            WAV 格式的音频字节数据
        """
        if not style_instruction:
            style_instruction = EMOTION_TO_STYLE.get(emotion, "用自然平稳的语调朗读")

        completion = self.client.chat.completions.create(
            model=self.preset_model,
            messages=[
                {"role": "user", "content": style_instruction},
                {"role": "assistant", "content": text},
            ],
            audio={"format": "wav", "voice": voice_id},
        )

        audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        return audio_bytes

    def synthesize_with_voice_design(
        self,
        text: str,
        voice_description: str,
        emotion: str = "neutral",
    ) -> bytes:
        """
        使用音色设计合成语音（多人模式）
        通过文本描述自动生成音色，每个角色都有独特的声音

        Args:
            text: 要合成的文字
            voice_description: 音色描述，如"一个20岁左右的年轻女性，声音甜美清脆，说话轻快活泼"
            emotion: 情绪标记

        Returns:
            WAV 格式的音频字节数据
        """
        style_instruction = EMOTION_TO_STYLE.get(emotion, "用自然平稳的语调朗读")

        completion = self.client.chat.completions.create(
            model=self.design_model,
            messages=[
                {"role": "user", "content": voice_description},
                {"role": "assistant", "content": text},
            ],
            audio={"format": "wav"},
        )

        audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        return audio_bytes

    def get_voice_options(self) -> dict:
        """获取可用预置音色列表"""
        return VOICE_OPTIONS

    def synthesize_with_clone(
        self,
        text: str,
        sample_audio_bytes: bytes,
        emotion: str = "neutral",
        style_instruction: str = "",
    ) -> bytes:
        """
        使用音频样本复刻音色合成语音

        Args:
            text: 要合成的文字
            sample_audio_bytes: 音频样本的原始字节（mp3 或 wav）
            emotion: 情绪标记
            style_instruction: 自定义风格指令

        Returns:
            WAV 格式的音频字节数据
        """
        if not style_instruction:
            style_instruction = EMOTION_TO_STYLE.get(emotion, "用自然平稳的语调朗读")

        # 编码音频样本为 base64 data URI
        sample_b64 = base64.b64encode(sample_audio_bytes).decode("utf-8")
        voice_data = f"data:audio/mpeg;base64,{sample_b64}"

        completion = self.client.chat.completions.create(
            model=self.clone_model,
            messages=[
                {"role": "user", "content": style_instruction},
                {"role": "assistant", "content": text},
            ],
            audio={"format": "wav", "voice": voice_data},
        )

        audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        return audio_bytes


# 全局单例
tts_service = TTSService()
