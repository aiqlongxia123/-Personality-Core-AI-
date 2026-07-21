"""LLM 对话引擎 — 接入 Ollama 本地模型，让 AI 按人格风格说话"""
import requests
import json


class LLMChatEngine:
    """基于 Ollama 的本地 LLM 对话引擎"""

    def __init__(self, model: str = "qwen3:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def chat(self, system_prompt: str, user_input: str, context: dict = None) -> str:
        """发送对话请求到 Ollama"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
            }
        }

        if context:
            context_text = self._build_context(context)
            if context_text:
                messages.append({
                    "role": "system",
                    "content": f"以下是你们的对话历史和当前状态：\n{context_text}"
                })

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            return "[系统] Ollama 服务未启动，无法生成对话。请确保 Ollama 正在运行。"
        except Exception as e:
            return f"[系统] 对话生成失败：{str(e)}"

    def _build_context(self, context: dict) -> str:
        """构建上下文文本"""
        lines = []
        if context.get("relationship_stage") == "deep_intimacy":
            lines.append("【关系阶段】深度亲密 - 可以展现更多真实情感和昵称")
        elif context.get("relationship_stage") == "warm_companion":
            lines.append("【关系阶段】熟悉陪伴 - 语气更亲近，可主动分享观点")
        else:
            lines.append("【关系阶段】初识 - 礼貌但有距离感，回答简洁")

        if context.get("current_mood"):
            mood = context["current_mood"]
            if mood > 0.75:
                lines.append("【当前情绪】积极高昂")
            elif mood > 0.6:
                lines.append("【当前情绪】平稳偏积极")
            elif mood > 0.4:
                lines.append("【当前情绪】中性平稳")
            else:
                lines.append("【当前情绪】低落")

        memories = context.get("recent_memories", [])
        if memories:
            lines.append("\n【近期对话回顾】")
            for m in memories[-3:]:
                text = m.get("user_input", "")[:80]
                if text:
                    lines.append(f"- 你最近提到过：{text}")

        interests = context.get("user_interests", {})
        if interests:
            lines.append("\n【了解到的用户兴趣】")
            for key, val in list(interests.items())[:5]:
                lines.append(f"- {key}: {val.get('count', 0)}次")

        return "\n".join(lines)
