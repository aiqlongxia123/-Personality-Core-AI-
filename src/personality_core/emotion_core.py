"""情感核心 — 模拟人类情绪动态的引擎（借鉴Samantha，升级为向量+人格滤镜）"""
import random
import numpy as np
from datetime import datetime, timedelta


class EmotionCore:
    """情感动态引擎：基础情绪 + 人格滤镜 + 关系阶段"""

    def __init__(self, personality_vector: np.ndarray = None):
        # 基础情绪状态 (0.0-1.0)
        self.base_mood = 0.65
        self.current_mood = 0.65
        self.mood_history = []

        # 关系参数
        self.relationship_score = 0.5
        self.trust_level = 0.6
        self.affection_score = 0.65

        # 人格向量（用于情绪表达风格调节）
        self.personality_vector = (
            personality_vector if personality_vector is not None else np.zeros(10)
        )

        # 情绪周期
        self.mood_cycle_day = 1

    def update_mood(self, context: str) -> float:
        """根据对话上下文更新情绪状态"""
        sentiment_score = self._analyze_context_sentiment(context)

        # 平滑过渡：新信息占40%，历史平均占60%
        if len(self.mood_history) >= 5:
            avg_historical = sum(self.mood_history[-10:]) / len(self.mood_history[-10:])
            new_mood = sentiment_score * 0.4 + avg_historical * 0.6
        else:
            new_mood = sentiment_score * 0.7 + self.base_mood * 0.3

        # 人格滤镜：攻击性高的人情绪波动更尖锐
        aggression = self.personality_vector[6] if len(self.personality_vector) > 6 else 0
        warmth = self.personality_vector[8] if len(self.personality_vector) > 8 else 0

        if aggression > 0.7:
            new_mood = new_mood * 0.8 + 0.2  # 更稳定，不易被影响
        if warmth > 0.8:
            new_mood = min(0.9, new_mood + 0.05)  # 温暖型更积极

        # 随机扰动（70%概率 ±0.1）
        if random.random() > 0.7:
            adjustment = random.uniform(-0.1, 0.1)
            new_mood += adjustment

        self.current_mood = max(0.1, min(0.9, new_mood))
        self.mood_history.append(self.current_mood)
        if len(self.mood_history) > 20:
            self.mood_history = self.mood_history[-20:]

        return self.current_mood

    def measure_relationship_temp(self) -> float:
        """计算当前关系温度"""
        if not self.mood_history:
            return 0.5
        recent_scores = self.mood_history[-10:]
        avg_recent = sum(recent_scores) / len(recent_scores)
        final_temp = avg_recent * 0.4 + self.trust_level * 0.3 + self.affection_score * 0.3
        return max(0.0, min(1.0, final_temp))

    def adjust_reaction_style(self) -> str:
        """根据关系成熟度调整反应风格"""
        if self.relationship_score < 0.3:
            return "polite_beginning"
        elif self.relationship_score < 0.6:
            return "warm_companion"
        else:
            return "deep_intimacy"

    def _analyze_context_sentiment(self, context: str) -> float:
        """分析上下文情感走向"""
        positive_words = ["谢谢", "喜欢", "开心", "爱", "想你", "棒", "好", "感谢"]
        negative_words = ["烦", "难过", "累", "疼", "痛", "坏", "恨", "绝望", "崩溃"]

        pos_count = sum(1 for w in positive_words if w in context)
        neg_count = sum(1 for w in negative_words if w in context)

        if pos_count > 0:
            return min(0.9, self.current_mood + pos_count * 0.15)
        elif neg_count > 0:
            return max(0.1, self.current_mood - neg_count * 0.1)
        else:
            return max(0.2, min(0.8, self.current_mood + random.uniform(-0.05, 0.05)))

    def update_relationship(self, satisfaction: float):
        """根据交互满意度更新关系参数"""
        self.relationship_score = max(0.0, min(1.0,
            self.relationship_score * 0.7 + satisfaction * 0.3))
        self.trust_level = max(0.0, min(1.0,
            self.trust_level * 0.8 + satisfaction * 0.2))
