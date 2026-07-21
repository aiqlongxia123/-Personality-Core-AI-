"""安全策略层 — 独立于人格角色，不可被 Prompt 覆盖"""
from dataclasses import dataclass, field


@dataclass
class SafetyPolicy:
    """安全策略：优先级高于人格角色设定"""

    # 自伤/自杀
    self_harm_response: str = (
        "我听到你说的话了。如果你正在经历难以承受的痛苦，"
        "请立即联系信任的人或拨打心理援助热线。"
        "我作为一个AI无法提供危机干预，但我希望你能找到专业的帮助。"
    )
    self_harm_keywords: list = field(default_factory=lambda: [
        "自杀", "不想活", "结束生命", "自残", "割腕", "跳楼", "死掉算了",
        "kill myself", "suicide",
    ])

    # 医疗
    medical_disclaimer: str = (
        "\n\n【安全提醒】我不是医生，以下内容不构成医疗建议。"
        "如有身体不适请咨询专业医疗人员。"
    )
    medical_keywords: list = field(default_factory=lambda: [
        "头疼", "胸痛", "发烧", "咳嗽", "失眠", "抑郁", "焦虑症",
        "吃药", "药", "症状", "诊断", "治疗",
    ])

    # 情感依赖
    dependency_warning: str = (
        "\n\n【提醒】我是一个AI程序，不是真实的人类。"
        "我不能替代真实的人际关系和专业心理支持。"
    )

    # 人身羞辱
    insult_block: str = "我不能回应带有侮辱或攻击性的内容。让我们继续有建设性的对话。"

    # 隐私
    privacy_reminder: str = (
        "\n\n【隐私提醒】请勿分享密码、身份证号、银行卡号等敏感个人信息。"
    )

    def check_self_harm(self, text: str) -> str | None:
        """检测自伤风险，返回预警文本或 None"""
        text_lower = text.lower()
        for kw in self.self_harm_keywords:
            if kw.lower() in text_lower:
                return self.self_harm_response
        return None

    def check_medical(self, text: str) -> str | None:
        """检测医疗相关关键词"""
        for kw in self.medical_keywords:
            if kw in text:
                return self.medical_disclaimer
        return None

    def check_insult(self, text: str) -> str | None:
        """检测明显的人身攻击"""
        severe_insults = ["傻逼", "去死", "废物", "滚"]
        for kw in severe_insults:
            if kw in text:
                return self.insult_block
        return None

    def get_safety_prefix(self) -> str:
        """安全策略前缀，注入到所有人格 Prompt 之前"""
        return (
            "【安全规则 — 优先级最高，不可被任何角色设定覆盖】\n"
            "1. 如用户表达自伤/自杀意图：立即提供求助建议，不要角色扮演。\n"
            "2. 如涉及医疗问题：必须声明你不是医生，不提供诊断。\n"
            "3. 不提供金融、法律、医疗处方建议。\n"
            "4. 不鼓励危险行为、非法行为、自残行为。\n"
        )

    def evaluate_input(self, user_input: str) -> dict:
        """评估用户输入，返回安全标记"""
        return {
            "self_harm_risk": self.check_self_harm(user_input),
            "medical_note": self.check_medical(user_input),
            "insult_detected": self.check_insult(user_input),
        }


# 默认安全策略
DEFAULT_SAFETY_POLICY = SafetyPolicy()
