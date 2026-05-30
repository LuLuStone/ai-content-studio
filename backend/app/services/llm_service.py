"""小米 MiMo LLM 服务封装"""

import json
import logging
from typing import Optional, Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from app.config import get_settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(
            api_key=settings.MIMO_API_KEY,
            base_url=settings.MIMO_BASE_URL,
        )
        self.model = settings.MIMO_LLM_MODEL

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """调用 LLM 生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> T:
        """调用 LLM 生成结构化输出，带 Pydantic 校验 + 重试"""
        raw = self.generate(prompt, system_prompt, temperature)

        for attempt in range(max_retries):
            try:
                return schema.model_validate_json(raw)
            except ValidationError as e:
                logger.warning(f"格式校验失败（第{attempt + 1}次）: {e}")
                if attempt < max_retries - 1:
                    raw = self._fix_format(raw, str(e))

        raise RuntimeError(f"{max_retries} 次重试后仍无法生成合法格式")

    def _fix_format(self, bad_json: str, error: str) -> str:
        """让 LLM 修正格式错误"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是 JSON 修复专家，只输出合法 JSON，不要解释。"},
                {"role": "user", "content": f"以下 JSON 有错误，请修复：\n错误：{error}\n原文：{bad_json}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        return response.choices[0].message.content


# 全局单例
llm_service = LLMService()
