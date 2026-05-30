"""播客脚本生成 Prompt 模板"""

PODCAST_SCRIPT_PROMPT = """
你是一个专业的播客脚本编剧。

请根据以下主题，生成一段 {speaker_count} 人对话的播客脚本。

【主题】
{user_input}

【播客风格】
{style}

【角色要求】
{speaker_requirements}

【严格输出要求】
1. 输出必须是合法的 JSON，不要包含任何 JSON 之外的文字
2. 每段对话必须包含以下字段：
   - speaker: 说话人名字
   - role: 角色定位（主持人/嘉宾/专家等）
   - text: 对话内容（自然口语，不要书面语）
   - emotion: 情绪标记，值为以下之一：neutral, happy, excited, serious, surprised, thoughtful, sad, angry, curious, lively, narrative, calm, warm, humorous, anxious, nostalgic, proud, worried, confident
3. 对话总段数在 {min_turns} 到 {max_turns} 之间
4. 第一段必须是主持人开场白
5. 最后一段必须是结束语
6. 对话要自然流畅，有来有回，像真实的播客对话

【输出 JSON 格式，必须严格遵守】
{{
  "title": "播客标题（简洁有力）",
  "description": "一句话简介",
  "speakers": [
    {{"name": "小明", "role": "主持人", "voice_id": "冰糖"}},
    {{"name": "小红", "role": "嘉宾", "voice_id": "苏打"}}
  ],
  "script": [
    {{
      "speaker": "小明",
      "role": "主持人",
      "text": "大家好，欢迎收听本期播客！今天我们来聊聊...",
      "emotion": "happy"
    }},
    {{
      "speaker": "小红",
      "role": "嘉宾",
      "text": "谢谢邀请！很高兴来到这里...",
      "emotion": "excited"
    }}
  ]
}}
"""

# 默认角色配置
DEFAULT_SPEAKER_CONFIGS = {
    2: [
        {"name": "主持人", "role": "主持人", "voice_id": "冰糖"},
        {"name": "嘉宾", "role": "嘉宾", "voice_id": "苏打"},
    ],
    3: [
        {"name": "主持人", "role": "主持人", "voice_id": "冰糖"},
        {"name": "嘉宾A", "role": "嘉宾", "voice_id": "苏打"},
        {"name": "嘉宾B", "role": "嘉宾", "voice_id": "茉莉"},
    ],
    4: [
        {"name": "主持人", "role": "主持人", "voice_id": "冰糖"},
        {"name": "嘉宾A", "role": "嘉宾", "voice_id": "苏打"},
        {"name": "嘉宾B", "role": "嘉宾", "voice_id": "茉莉"},
        {"name": "嘉宾C", "role": "嘉宾", "voice_id": "白桦"},
    ],
}
