"""有声书脚本生成 Prompt 模板"""

AUDIOBOOK_MULTI_PROMPT = """
你是一个专业的有声书制作助手。

请分析以下文本，识别其中的所有角色，并生成带角色标注的朗读脚本。

【文本内容】
{user_input}

【朗读风格】
{style}

【要求】
1. 识别文本中所有说话的角色（旁白也算一个角色）
2. 为每个角色推断性别和年龄段（男/女 + 少年/青年/中年/老年）
3. 为每个角色生成一段音色描述（用于 AI 语音合成时设计独特音色）
4. 将文本按对话和旁白拆分成段落
5. 每段标注情绪
6. 输出合法 JSON

【音色描述要求】
- 描述要具体生动，包含年龄、性别、音色特点、说话习惯
- 每个角色的音色要有明显区别
- 示例："一个40岁左右的中年男性，声音低沉浑厚，说话沉稳有力，像新闻主播"
- 示例："一个8岁的小女孩，声音稚嫩清脆，说话奶声奶气，语速较快"
- 示例："旁白，一个30岁左右的女性，声音温柔沉稳，像纪录片解说"

【输出格式】
{{
  "title": "作品标题",
  "characters": [
    {{"name": "旁白", "gender": "female", "age_group": "青年", "voice_id": "voice_design", "voice_description": "一个30岁左右的女性，声音温柔沉稳，语速适中，像纪录片解说"}},
    {{"name": "林黛玉", "gender": "female", "age_group": "青年", "voice_id": "voice_design", "voice_description": "一个16岁的少女，声音清脆柔弱，说话轻声细语，带着一丝忧郁"}},
    {{"name": "贾宝玉", "gender": "male", "age_group": "青年", "voice_id": "voice_design", "voice_description": "一个18岁的少年，声音清朗温润，说话时带着少年意气和几分不羁"}}
  ],
  "segments": [
    {{"character": "旁白", "text": "话说那日，宝玉正在园中闲逛...", "emotion": "neutral"}},
    {{"character": "贾宝玉", "text": "林妹妹，你怎的又在此处伤心？", "emotion": "surprised"}},
    {{"character": "林黛玉", "text": "我哪里伤心了，不过是风沙迷了眼。", "emotion": "sad"}}
  ]
}}

【可用情绪值】neutral, happy, excited, serious, surprised, thoughtful, sad, angry, curious, lively, narrative, calm, warm, humorous, anxious, nostalgic, proud, worried, confident
"""

AUDIOBOOK_SINGLE_PROMPT = """
你是一个专业的有声书制作助手。

请将以下文本整理为适合朗读的格式，按段落拆分，标注情绪。

【文本内容】
{user_input}

【朗读风格】
{style}

【要求】
1. 按自然段落拆分
2. 每段标注适合的情绪
3. 输出合法 JSON

【输出格式】
{{
  "title": "作品标题",
  "characters": [
    {{"name": "朗读者", "gender": "female", "age_group": "青年", "voice_id": "{voice_id}", "voice_description": ""}}
  ],
  "segments": [
    {{"character": "朗读者", "text": "段落内容...", "emotion": "neutral"}},
    {{"character": "朗读者", "text": "段落内容...", "emotion": "happy"}}
  ]
}}

【可用情绪值】neutral, happy, excited, serious, surprised, thoughtful, sad, angry, curious, lively, narrative, calm, warm, humorous, anxious, nostalgic, proud, worried, confident
"""

# 音色自动匹配（单人模式用）
VOICE_AUTO_MATCH = {
    ("male", "少年"): "苏打",
    ("male", "青年"): "苏打",
    ("male", "中年"): "白桦",
    ("male", "老年"): "白桦",
    ("female", "少年"): "冰糖",
    ("female", "青年"): "冰糖",
    ("female", "中年"): "茉莉",
    ("female", "老年"): "茉莉",
}
