"""情感核心 — 模拟人类情绪动态的引擎"""
import random
import numpy as np


class EmotionCore:
    """情感动态引擎：基础情绪 + 人格特质滤镜 + 关系阶段。

    mood（情绪状态）、satisfaction（交互满意度）、relationship（关系深度）
    三者独立演变，互不替代。
    """

    def __init__(
        self,
        personality_vector: np.ndarray = None,
        traits: dict = None,
    ):
        # 基础情绪状态 (0.0-1.0)
        self.base_mood = 0.65
        self.current_mood = 0.65
        self.mood_history = []

        # 交互满意度（本次交互质量，独立于长期情绪）
        self.satisfaction = 0.5

        # 关系参数（信任+亲密度，慢变量）
        self.relationship_score = 0.5
        self.trust_level = 0.6
        self.affection_score = 0.65

        # 人格向量（ICA因子得分）
        self.personality_vector = (
            personality_vector if personality_vector is not None else np.zeros(10)
        )

        # 人格特质
        self.traits = traits or {}
        self._aggression = float(self.traits.get("aggression", 0.0))
        self._warmth = float(self.traits.get("warmth", 0.0))

    def update_mood(self, context: str) -> float:
        """根据对话上下文更新情绪状态。返回当前情绪值。"""
        sentiment_score = self._analyze_context_sentiment(context)

        # 平滑过渡
        if len(self.mood_history) >= 5:
            avg_historical = sum(self.mood_history[-10:]) / len(self.mood_history[-10:])
            new_mood = sentiment_score * 0.4 + avg_historical * 0.6
        else:
            new_mood = sentiment_score * 0.7 + self.base_mood * 0.3

        # 人格滤镜
        if self._aggression > 0.7:
            new_mood = new_mood * 0.8 + 0.2
        if self._warmth > 0.8:
            new_mood = min(0.9, new_mood + 0.05)

        # 随机扰动（30%概率）
        if random.random() < 0.3:
            new_mood += random.uniform(-0.1, 0.1)

        self.current_mood = max(0.1, min(0.9, new_mood))
        self.mood_history.append(self.current_mood)
        if len(self.mood_history) > 20:
            self.mood_history = self.mood_history[-20:]

        return self.current_mood

    def evaluate_satisfaction(self, context: str) -> float:
        """评估本次交互的满意度（独立于情绪状态）。

        满意度反映对话质量：是否有实质性交流、是否被理解、是否有趣。
        用户表达痛苦时，满意度反映的是"交流有效程度"而非"用户心情好坏"。
        """
        # 基础分
        base = 0.5

        # 长度加分：有内容的对话
        text_len = len(context)
        if text_len >= 10:
            base += 0.05
        if text_len >= 20:
            base += 0.05
        if text_len >= 50:
            base += 0.05
        if text_len >= 100:
            base += 0.05

        # 提问加分
        question_markers = ["?", "？", "为什么", "怎么", "什么", "如何"]
        if any(m in context for m in question_markers):
            base += 0.1

        # 情感表达加分（无论正负面）
        emotion_words = [
            "觉得", "感觉", "想", "怕", "担心", "开心", "难过",
            "迷茫", "烦", "累", "喜欢", "恨", "爱",
        ]
        emotion_count = sum(1 for w in emotion_words if w in context)
        if emotion_count > 0:
            base += min(0.15, emotion_count * 0.05)

        # 温暖型人格对满意度感知更高
        if self._warmth > 0.7:
            base += 0.05

        self.satisfaction = max(0.1, min(0.9, base))
        return self.satisfaction

    def update_relationship(self, satisfaction: float):
        """根据交互满意度更新关系参数（慢变量）。"""
        self.relationship_score = max(0.0, min(1.0,
            self.relationship_score * 0.85 + satisfaction * 0.15))
        self.trust_level = max(0.0, min(1.0,
            self.trust_level * 0.9 + satisfaction * 0.1))

    def measure_relationship_temp(self) -> float:
        """计算当前关系温度"""
        if not self.mood_history:
            return 0.5
        recent_scores = self.mood_history[-10:]
        avg_recent = sum(recent_scores) / len(recent_scores)
        return max(0.0, min(1.0, avg_recent * 0.3 + self.trust_level * 0.4 + self.affection_score * 0.3))

    def adjust_reaction_style(self) -> str:
        """根据关系成熟度调整反应风格"""
        if self.relationship_score < 0.3:
            return "polite_beginning"
        elif self.relationship_score < 0.6:
            return "warm_companion"
        else:
            return "deep_intimacy"

    # ═══════════════ 情感分析（jieba 分词） ═══════════════

    def _analyze_context_sentiment(self, context: str) -> float:
        """用 jieba 分词 + 否定检测分析情感走向"""
        try:
            import jieba
            tokens = list(jieba.cut(context))
        except ImportError:
            tokens = list(context)

        positive_words = {"谢谢", "喜欢", "开心", "爱", "想你", "棒", "好", "感谢"}
        negative_words = {
            "烦", "难过", "累", "疼", "痛", "恨", "绝望", "崩溃",
            "不好", "不太好", "不够好", "不开心",  # 复合否定词直接标注为负面
        }
        negation_words = {"不", "没", "别", "未", "无", "非"}

        pos_count = 0
        neg_count = 0
        negated = False

        for token in tokens:
            token = token.strip()
            if not token:
                continue

            # 复合否定词直接计为负面
            if token in {"不好", "不太好", "不够好", "不开心", "不爱", "不喜欢"}:
                neg_count += 1
                negated = False
                continue

            # 检测否定词
            if token in negation_words:
                negated = True
                continue

            if token in positive_words:
                if negated:
                    neg_count += 1
                else:
                    pos_count += 1
                negated = False
            elif token in negative_words:
                if negated:
                    pos_count += 1
                else:
                    neg_count += 1
                negated = False
            elif token in {"太", "很", "非常", "有点", "有些"}:
                pass
            else:
                negated = False

        if pos_count > 0 and neg_count > 0:
            delta = pos_count * 0.08 - neg_count * 0.12
            return max(0.1, min(0.9, self.current_mood + delta))
        elif pos_count > 0:
            return min(0.9, self.current_mood + pos_count * 0.12)
        elif neg_count > 0:
            return max(0.1, self.current_mood - neg_count * 0.15)
        else:
            return max(0.1, min(0.9, self.current_mood + __import__('random').uniform(-0.05, 0.05)))
