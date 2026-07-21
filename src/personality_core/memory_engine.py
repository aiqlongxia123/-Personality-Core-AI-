"""记忆与成长引擎 — 三层记忆系统（借鉴Samantha，升级为触发演化）"""
import json
from pathlib import Path
from datetime import datetime, timedelta
import collections


class MemoryAndGrowthEngine:
    """管理记忆、关系演进和成长日志的系统"""

    def __init__(self, data_dir: str = "./memory_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 三层记忆存储
        self.sensory_memories = []       # 短期：最近30条
        self.interaction_logs = []       # 长期：全部交互记录
        self.milestone_events = []       # 里程碑事件
        self.growth_log = collections.OrderedDict()
        self.relationship_milestones = collections.OrderedDict()

        self._load_stored_data()

    def _load_stored_data(self):
        memories_file = self.data_dir / "relationships.json"
        try:
            if memories_file.exists():
                with open(memories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.interaction_logs = data.get('interactions', [])
                self.milestone_events = data.get('milestones', [])
                self.sensory_memories = data.get('sensory', [])
                self.growth_log = collections.OrderedDict(data.get('growth', []))
        except Exception as e:
            print(f"加载记忆数据时出错：{e}")

    def store_interaction(self, interaction: dict):
        """存储一次交互并分析影响"""
        interaction['timestamp'] = datetime.now().isoformat()
        interaction['id'] = len(self.interaction_logs) + 1

        # 存入短期记忆
        self.sensory_memories.append(interaction)
        if len(self.sensory_memories) > 30:
            self.sensory_memories = self.sensory_memories[-30:]

        # 存入长期记忆
        self.interaction_logs.append(interaction)

        # 分析是否为重要事件
        satisfaction = interaction.get('satisfaction_score', 0.5)
        if satisfaction >= 0.8:
            interaction['milestone_type'] = 'positive_moment'
            self._mark_milestone(event=interaction, type='positive_moment')
        elif satisfaction <= 0.2:
            interaction['milestone_type'] = 'negative_moment'
            self._mark_milestone(event=interaction, type='negative_moment')

        # 检测用户兴趣模式
        self._track_user_interests(interaction)

        self._save_data()

    def _mark_milestone(self, event, type: str):
        event['milestone_type'] = type
        event['recognized_at'] = datetime.now().isoformat()
        self.milestone_events.append(event)

        milestone_key = f"第{len(self.relationship_milestones)+1}个重要时刻"
        if len(self.relationship_milestones) < 20:
            self.relationship_milestones[milestone_key] = event

    def _track_user_interests(self, interaction: dict):
        text = interaction.get('user_input', '')
        interest_map = {
            '研究': 'tech_research',
            '学术': 'academic',
            '头疼': 'health_concerns',
            '难过': 'emotional_support',
            '未来': 'future_planning',
            '书': 'reading',
            '代码': 'coding',
        }
        for keyword, interest in interest_map.items():
            if keyword in text:
                key = f"interest_{interest}"
                if key not in self.growth_log:
                    self.growth_log[key] = {"discovered_at": datetime.now().isoformat(), "count": 1}
                else:
                    self.growth_log[key]["count"] += 1

    def get_recent_memories(self, n: int = 5) -> list:
        """获取最近N条短期记忆"""
        return self.sensory_memories[-n:]

    def get_user_interests(self) -> dict:
        """获取用户兴趣画像"""
        return dict(self.growth_log)

    def generate_weekly_story(self) -> str:
        last_week = datetime.now() - timedelta(days=7)
        important = [i for i in self.interaction_logs
                     if datetime.fromisoformat(i["timestamp"]) > last_week]

        lines = [
            f"🌹 {datetime.now().strftime('%Y/%m/%d')} 周度故事",
            "",
            "1. 我们这一周...",
        ]
        for i, event in enumerate(important[:5], 1):
            text = event.get('user_input', '')[:50] + "..."
            timestamp = event['timestamp'][:10]
            lines.append(f"   {i}. [{timestamp}] {text}")

        lines.extend([
            "",
            f"2. 当前关系状态：{self._calculate_metrics():.1f}",
        ])
        return "\n".join(lines)

    def _calculate_metrics(self) -> float:
        if not self.interaction_logs:
            return 0.5
        recent = [e.get('satisfaction_score', 0.5) for e in self.interaction_logs[-10:]]
        return sum(recent) / len(recent)

    def _save_data(self):
        data = {
            'interactions': self.interaction_logs,
            'milestones': self.milestone_events,
            'sensory': self.sensory_memories,
            'growth': list(self.growth_log.items()),
            'relationship_milestones': dict(self.relationship_milestones),
        }
        try:
            with open(self.data_dir / "relationships.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆数据失败：{e}")
