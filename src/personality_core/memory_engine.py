"""记忆与成长引擎 — SQLite 三层记忆系统"""
import json
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict


class MemoryAndGrowthEngine:
    """管理记忆、关系演进和成长日志（SQLite 后端，线程安全）"""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_input TEXT,
        response TEXT,
        mood REAL,
        stage TEXT,
        satisfaction_score REAL DEFAULT 0.5
    );
    CREATE TABLE IF NOT EXISTS milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interaction_id INTEGER,
        milestone_type TEXT,
        recognized_at TEXT NOT NULL,
        FOREIGN KEY (interaction_id) REFERENCES interactions(id)
    );
    CREATE TABLE IF NOT EXISTS interests (
        key TEXT PRIMARY KEY,
        discovered_at TEXT NOT NULL,
        count INTEGER DEFAULT 1
    );
    CREATE INDEX IF NOT EXISTS idx_interactions_ts ON interactions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_interactions_stage ON interactions(stage);
    """

    def __init__(
        self,
        data_dir: str = "./memory_data",
        max_interactions: int = 10000,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.max_interactions = max_interactions

        self._db_path = self.data_dir / "memory.db"
        self._local = threading.local()

        # 运行时缓存
        self.sensory_memories: list[dict] = []
        self.growth_log: OrderedDict = OrderedDict()
        self.relationship_milestones: OrderedDict = OrderedDict()
        
        # 学习演化相关
        self.relationship_strength: float = 0.5
        self.interaction_count: int = 0
        self.current_topic_priority: str | None = None
        self.prev_trend: str | None = None
        self._prev_relationship: float = 0.5

        self._init_db()
        self._load_cache()

    # ═══════════════ DB 连接 ═══════════════

    def _get_conn(self) -> sqlite3.Connection:
        """线程本地 SQLite 连接（WAL 模式）"""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        conn.executescript(self._SCHEMA)
        conn.commit()

    def _load_cache(self):
        """从 DB 加载最近数据到内存缓存"""
        conn = self._get_conn()
        # 最近 30 条为短期记忆
        rows = conn.execute(
            "SELECT * FROM interactions ORDER BY id DESC LIMIT 30"
        ).fetchall()
        self.sensory_memories = [dict(r) for r in reversed(rows)]

        # 兴趣
        rows = conn.execute("SELECT * FROM interests").fetchall()
        self.growth_log = OrderedDict()
        for r in rows:
            self.growth_log[r["key"]] = {
                "discovered_at": r["discovered_at"],
                "count": r["count"],
            }

    # ═══════════════ 存储 ═══════════════

    def store_interaction(self, interaction: dict):
        """存储一次交互（SQLite 事务写入）"""
        conn = self._get_conn()
        now = datetime.now().isoformat()

        try:
            with conn:
                cur = conn.execute(
                    """INSERT INTO interactions
                       (timestamp, user_input, response, mood, stage, satisfaction_score)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        now,
                        interaction.get("user_input", ""),
                        interaction.get("response"),
                        interaction.get("mood"),
                        interaction.get("stage"),
                        interaction.get("satisfaction_score", 0.5),
                    ),
                )
                interaction_id = cur.lastrowid
        except Exception as e:
            print(f"存储交互失败: {e}")
            return

        # 更新短期记忆
        interaction["id"] = interaction_id
        interaction["timestamp"] = now
        self.sensory_memories.append(interaction)
        if len(self.sensory_memories) > 30:
            self.sensory_memories = self.sensory_memories[-30:]

        # 里程碑检测
        satisfaction = interaction.get("satisfaction_score", 0.5)
        if satisfaction >= 0.8:
            self._mark_milestone(interaction_id, "positive_moment")
        elif satisfaction <= 0.2:
            self._mark_milestone(interaction_id, "negative_moment")

        # 兴趣追踪
        self._track_user_interests(interaction)

        # 定期清理旧数据
        self._maybe_prune()

    def _mark_milestone(self, interaction_id: int, mtype: str):
        conn = self._get_conn()
        now = datetime.now().isoformat()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO milestones (interaction_id, milestone_type, recognized_at) VALUES (?, ?, ?)",
                    (interaction_id, mtype, now),
                )
        except Exception:
            pass

        milestone_key = f"第{len(self.relationship_milestones)+1}个重要时刻"
        if len(self.relationship_milestones) < 20:
            self.relationship_milestones[milestone_key] = {
                "interaction_id": interaction_id,
                "type": mtype,
                "recognized_at": now,
            }

    def _track_user_interests(self, interaction: dict):
        text = interaction.get("user_input", "")
        interest_map = {
            "研究": "tech_research",
            "学术": "academic",
            "头疼": "health_concerns",
            "难过": "emotional_support",
            "未来": "future_planning",
            "书": "reading",
            "代码": "coding",
        }
        conn = self._get_conn()
        for keyword, interest in interest_map.items():
            if keyword in text:
                key = f"interest_{interest}"
                try:
                    with conn:
                        conn.execute(
                            """INSERT INTO interests (key, discovered_at, count)
                               VALUES (?, ?, 1)
                               ON CONFLICT(key) DO UPDATE SET count = count + 1""",
                            (key, datetime.now().isoformat()),
                        )
                except Exception:
                    pass
                if key in self.growth_log:
                    self.growth_log[key]["count"] += 1
                else:
                    self.growth_log[key] = {
                        "discovered_at": datetime.now().isoformat(),
                        "count": 1,
                    }

    def _maybe_prune(self):
        """定期清理：保留最近 max_interactions 条"""
        conn = self._get_conn()
        try:
            count = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
            if count > self.max_interactions:
                cutoff_id = conn.execute(
                    "SELECT id FROM interactions ORDER BY id DESC LIMIT 1 OFFSET ?",
                    (self.max_interactions,),
                ).fetchone()
                if cutoff_id:
                    with conn:
                        conn.execute(
                            "DELETE FROM interactions WHERE id < ?",
                            (cutoff_id["id"],),
                        )
        except Exception:
            pass

    # ═══════════════ 学习演化 ═══════════════

    def analyze_and_learn(self, user_input: str, response: str) -> dict:
        """分析对话并学习演化：更新情绪记录，触发人格微调"""
        emotions = self._analyze_emotions(user_input, response)
        
        # 关系强度根据情绪信号动态调整
        if emotions['tension'] > 0.4:
            self.relationship_strength += 0.01
        elif emotions['warmth'] > 0.6:
            self.relationship_strength += 0.005
        elif emotions['sadness'] > 0.5:
            self.relationship_strength -= 0.002
        
        # 限制在合理范围
        self.relationship_strength = max(0.0, min(1.0, self.relationship_strength))
        
        # 交互计数 + 定期整合
        self.interaction_count += 1
        if self.interaction_count % 10 == 0:
            self._consolidate_memories()
        
        return {
            "emotions": emotions,
            "relationship_delta": self.relationship_strength,
            "interaction_count": self.interaction_count,
        }

    def _analyze_emotions(self, input_text: str, response_text: str) -> dict:
        """分析对话中的情绪信号"""
        warmth_signals = ['谢谢', '开心', '爱', '温暖', '感动', '感谢', '喜欢', '舒服']
        tension_signals = ['生气', '愤怒', '错误', '不对', '反驳', '质疑', '矛盾', '讨厌']
        sadness_signals = ['难过', '伤心', '哭', '失望', '痛苦', '孤独', '抑郁', '绝望']
        curiosity_signals = ['好奇', '为什么', '怎么', '如何', '探索', '发现', '学习']
        
        def count_matches(signals: list, text: str) -> float:
            matches = sum(1 for s in signals if s in text.lower())
            return min(matches / max(len(signals), 1), 1.0)
        
        warmth = count_matches(warmth_signals, input_text + response_text)
        tension = count_matches(tension_signals, input_text)
        sadness = count_matches(sadness_signals, input_text)
        curiosity = count_matches(curiosity_signals, input_text)
        
        return {
            "warmth": round(warmth, 4),
            "tension": round(tension, 4),
            "sadness": round(sadness, 4),
            "curiosity": round(curiosity, 4),
        }

    def _consolidate_memories(self):
        """记忆整合：将近期记忆压缩为长期模式"""
        recent = self.get_recent_memories(10)
        
        if len(recent) < 3:
            return
        
        # 提取高频关键词和主题
        topics = {}
        for mem in recent:
            text = mem.get('user_input', '') or ''
            for word in self._topic_keywords:
                if word in text:
                    topics[word] = topics.get(word, 0) + 1
        
        if topics:
            top_topic = max(topics, key=topics.get)
            self.current_topic_priority = top_topic
            print(f"[记忆整合] 高频话题: {top_topic} ({topics[top_topic]}次)")
        
        # 更新关系强度缓存
        if hasattr(self, '_prev_relationship'):
            self._prev_relationship = self.relationship_strength
    
    def _track_growth_pattern(self):
        """追踪成长模式（基于交互历史）"""
        conn = self._get_conn()
        try:
            # 统计平均满意度变化趋势
            recent_rows = conn.execute(
                "SELECT satisfaction_score FROM interactions ORDER BY id DESC LIMIT 20"
            ).fetchall()
            
            if len(recent_rows) >= 5:
                recent_scores = [r[0] for r in recent_rows[:10]]
                older_scores = [r[0] for r in recent_rows[10:]]
                
                avg_recent = sum(recent_scores) / len(recent_scores)
                avg_older = sum(older_scores) / len(older_scores)
                
                trend = "improving" if avg_recent > avg_older else "declining" if avg_recent < avg_older else "stable"
                
                if trend != getattr(self, 'prev_trend', None):
                    print(f"[成长趋势] {self.prev_trend or 'initial'} → {trend}")
                    self.prev_trend = trend
        except Exception:
            pass

    # 初始化时添加的关键词池
    _topic_keywords = [
        '研究', '学术', '技术', '未来', '科学', '爱情', '家庭', '工作', 
        '梦想', '旅行', '电影', '音乐', '阅读', '思考', '人生', '哲学',
        '艺术', '创作', '设计', '编程', '运动', '健康', '美食', '宠物'
    ]

    # ═══════════════ 读取 ═══════════════

    def get_recent_memories(self, n: int = 5) -> list:
        """获取最近 N 条短期记忆"""
        return self.sensory_memories[-n:]

    def get_user_interests(self) -> dict:
        """获取用户兴趣画像"""
        return dict(self.growth_log)

    def generate_weekly_story(self) -> str:
        """生成周度故事"""
        conn = self._get_conn()
        last_week = (datetime.now() - timedelta(days=7)).isoformat()
        rows = conn.execute(
            "SELECT * FROM interactions WHERE timestamp > ? ORDER BY id DESC LIMIT 5",
            (last_week,),
        ).fetchall()

        lines = [
            f"🌹 {datetime.now().strftime('%Y/%m/%d')} 周度故事",
            "",
            "1. 我们这一周...",
        ]
        for i, event in enumerate(rows, 1):
            text = (event["user_input"] or "")[:50]
            if len(text) >= 50:
                text += "..."
            timestamp = event["timestamp"][:10]
            lines.append(f"   {i}. [{timestamp}] {text}")

        metrics = self._calculate_metrics()
        lines.extend(["", f"2. 当前关系状态：{metrics:.1f}"])
        return "\n".join(lines)

    def _calculate_metrics(self) -> float:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT satisfaction_score FROM interactions ORDER BY id DESC LIMIT 10"
        ).fetchall()
        if not rows:
            return 0.5
        return sum(r["satisfaction_score"] for r in rows) / len(rows)

    # ═══════════════ 清理 ═══════════════

    def clear_all(self):
        """清空所有记忆（慎用）"""
        conn = self._get_conn()
        with conn:
            conn.execute("DELETE FROM interactions")
            conn.execute("DELETE FROM milestones")
            conn.execute("DELETE FROM interests")
        self.sensory_memories = []
        self.growth_log = OrderedDict()

    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
