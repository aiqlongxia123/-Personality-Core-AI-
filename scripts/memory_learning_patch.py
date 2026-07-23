"""
2. memory_engine 对话学习机制升级
让记忆引擎在对话后分析情绪变化、更新人格参数
"""

# 在 memory_engine.py 中添加学习演化函数


LEARNING_METHODS = """
def analyze_and_learn(self, user_input: str, response: str) -> dict:
    \"\"\"分析对话并学习演化：更新情绪记录，触发人格微调\"\"\"
    
    # 1. 情绪分析（简单关键词匹配 + 上下文）
    emotions = self._analyze_emotions(user_input, response)
    
    # 2. 关系强度更新
    if emotions['tension'] > 0.5:
        self.relationship_strength += 0.01  # 冲突增多关系加深
    elif emotions['warmth'] > 0.7:
        self.relationship_strength += 0.005  # 温暖促进亲密
    
    # 3. 记忆密度更新
    self.interaction_count += 1
    if self.interaction_count % 10 == 0:
        self._consolidate_memories()
    
    # 4. 生成报告
    return {
        "emotions": emotions,
        "relationship_delta": self.relationship_strength - self.prev_relationship,
        "memory_density": self.memory_density(),
    }

def _analyze_emotions(self, input_text: str, response_text: str) -> dict:
    \"\"\"分析对话中的情绪信号\"\"\"
    warmth_signals = ['谢谢', '开心', '爱', '温暖', '感动', '感谢']
    tension_signals = ['生气', '愤怒', '错误', '不对', '反驳', '质疑']
    sadness_signals = ['难过', '伤心', '哭', '失望', '痛苦', '孤独']
    
    warmth = sum(1 for s in warmth_signals if s in input_text.lower()) / max(len(warmth_signals), 1)
    tension = sum(1 for s in tension_signals if s in input_text.lower()) / max(len(tension_signals), 1)
    sadness = sum(1 for s in sadness_signals if s in input_text.lower()) / max(len(sadness_signals), 1)
    
    return {
        "warmth": min(warmth * 2, 1.0),  # 归一化到 0-1
        "tension": min(tension * 2, 1.0),
        "sadness": min(sadness * 2, 1.0),
    }

def _consolidate_memories(self):
    \"\"\"记忆整合：将近期记忆压缩为长期模式\"\"\"
    if not hasattr(self, 'recent_memories'):
        self.recent_memories = []
    
    if len(self.recent_memories) >= 5:
        # 提取高频话题
        topics = [m.get('topic', '') for m in self.recent_memories[-5:]]
        top_topic = max(set(topics), key=topics.count)
        
        # 更新当前主题倾向
        self.current_topic_priority = top_topic
        
        # 清理过期记忆
        self.recent_memories = self.recent_memories[-2:]
        
        print(f\"[记忆整合] 高频话题: {top_topic}\")
"""
