# -*- coding: utf-8 -*-
"""
回答生成模块（FR-07）
====================
【检索生成阶段】将用户问题 + 检索/重排后的上下文片段组装为 Prompt，
调用 DeepSeek 大模型（OpenAI 兼容接口）生成回答。

Prompt 模板强制约束（抑制幻觉的关键）：
- 只能依据检索到的制度文档片段作答，禁止编造；
- 知识库没有对应信息时，必须直接回复"不知道"。
"""
from typing import List

from openai import OpenAI


class Generator:
    """DeepSeek 大模型生成器。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.0,
        system_prompt: str = "",
    ):
        if not api_key:
            raise ValueError(
                "[生成] 缺少 DEEPSEEK_API_KEY，请在 .env 中配置后重试"
            )
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._temperature = temperature
        self._system_prompt = system_prompt
        print(f"[生成] DeepSeek 模型：{model}（base_url={base_url}）")

    def generate(self, question: str, contexts: List[str]) -> str:
        """根据上下文片段生成回答。"""
        context_block = "\n\n".join(
            f"[文档片段 {i + 1}]\n{text}" for i, text in enumerate(contexts)
        )
        user_message = (
            "【检索到的制度文档片段】\n"
            f"{context_block}\n\n"
            f"【用户问题】\n{question}"
        )
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=self._temperature,
            stream=False,
        )
        return response.choices[0].message.content or ""
