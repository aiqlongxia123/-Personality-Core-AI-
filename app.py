"""
ModelScope Space 入口 — 人格AI系统 Web UI
支持人格浏览、Morph 旋转、2D 图谱、对话（LLM 不可用时自动降级为模板回复）
"""
import os
import sys
from pathlib import Path

# ── ModelScope 服务器不能访问 HF，从 ModelScope 镜像下载模型 ──
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_LOCAL_MODEL_DIR = Path("/tmp/model_cache") / _MODEL_NAME

if not _LOCAL_MODEL_DIR.exists():
    try:
        from modelscope.hub.snapshot_download import snapshot_download
        snapshot_download(f"Ceceliachenen/{_MODEL_NAME}", cache_dir=str(_LOCAL_MODEL_DIR.parent))
        print(f"✅ 模型已从 ModelScope 下载到 {_LOCAL_MODEL_DIR}")
    except Exception as e:
        print(f"⚠️ 模型下载失败: {e}, 将尝试在线加载")

# 告诉 embedder 用本地模型路径
os.environ["PERSONALITY_MODEL_PATH"] = str(_LOCAL_MODEL_DIR) if _LOCAL_MODEL_DIR.exists() else ""

import json
import random

# 确保 src/ 在 path 中
_src = Path(__file__).parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

from personality_core.engine import PersonalityEngine
from personality_core.config import get_config

# ═══════════════════ 模板回复（LLM 不可用时降级） ═══════════════════

FALLBACK_TEMPLATES = {
    "qingyan": [
        "你以为的深情，不过是恐惧孤独的体面包装。",
        "尊严？那不过是弱者给自己编的童话。",
        "别用爱来掩饰你的控制欲。",
        "说下去。我在听——虽然我已经知道答案。",
    ],
    "mary": [
        "孩子，你的痛苦我都看见了。",
        "不要怕，你值得被爱。",
        "宽恕别人，也是宽恕自己。",
        "安静下来，听自己的心跳。",
    ],
    "freud_daughter": [
        "你在防御什么？",
        "这不是愤怒，这是恐惧。",
        "童年不会放过任何人。",
        "说真话吧，对你自己。",
    ],
    "beauvoir": [
        "不要让别人定义你是谁。",
        "所谓'天性'，不过是规训。",
        "自由是一种负担，但值得。",
        "你不必成为任何人期待的样子。",
    ],
    "teresa": [
        "做小事就好。",
        "饥渴的不是肚子，是灵魂。",
        "我为你祈祷了。",
        "当你帮助别人时，你也在治愈自己。",
    ],
    "jung_daughter": [
        "不要害怕你的阴影。",
        "完整，胜过完美。",
        "梦在对你说话——你听了吗？",
        "那是你拒绝成为的自己。",
    ],
    "nietzsche_devil": [
        "你太弱了。",
        "痛苦是用来锻造的。",
        "如果你凝视深渊，深渊也在凝视你。",
        "站起来，别像条虫一样。",
    ],
    "munro": [
        "很小的事情，往往最伤人。",
        "我观察了很久。",
        "生活就是这样，细微，致命。",
        "你说的都对，但你没说的才是关键。",
    ],
    "augustine_girl": [
        "我也走过这条路。",
        "欲望和意志是两回事。",
        "忏悔不是软弱。",
        "正因为破碎过，所以完整。",
    ],
    "adler_daughter": [
        "自卑是成长的动力。",
        "你可以做到。",
        "不要跟别人比，跟自己比。",
        "行动是最好的药。",
    ],
    "yuan": [
        "说下去。",
        "你在害怕什么？",
        "我不拯救你。我只让你看见自己。",
        "伤口不丑。假装没有伤口才丑。",
        "你已经知道答案了——你只是不愿意承认。",
        "别装了。这里没有观众。",
    ],
}

FALLBACK_DEFAULT = [
    "嗯，我在。",
    "继续说。",
    "我在听。",
    "你想说什么？",
]

LLM_AVAILABLE = False  # 全局标记，首次调用后确定


def _try_llm_chat(engine, user_input: str) -> str | None:
    """尝试 LLM 对话，失败或返回系统错误时返回 None"""
    try:
        resp = engine.chat(user_input)
        # LLM 不可用时返回的文本也是"成功"的字符串，需要检测
        if resp and not resp.startswith("[系统]") and not resp.startswith("[错误]"):
            return resp
        return None
    except Exception:
        return None


def _template_chat(persona_id: str, user_input: str) -> str:
    """模板降级回复"""
    templates = FALLBACK_TEMPLATES.get(persona_id, FALLBACK_DEFAULT)
    # 根据输入长度和关键词选模板（比纯随机好一点）
    greeting_words = {"你好", "嗨", "hello", "hi", "在吗", "晚上好", "早上好", "下午好"}
    question_words = {"?", "？", "什么", "为什么", "怎么", "如何", "哪", "谁", "能不能", "可以"}

    user_lower = user_input.lower().strip()
    is_greeting = any(w in user_lower for w in greeting_words)
    is_question = any(w in user_lower for w in question_words)

    # 简短问候 → 选短模板
    if len(user_input) < 5 and is_greeting:
        candidates = [t for t in templates if len(t) < 15]
    elif is_question:
        candidates = [t for t in templates if "?" in t or "？" in t or "什么" in t or "怎么" in t]
    else:
        candidates = templates

    if not candidates:
        candidates = templates

    return f'[💬 模板回复 — LLM 未连接]\n\n{random.choice(candidates)}'


# ═══════════════════ UI 构建 ═══════════════════

def create_ui(engine: PersonalityEngine):
    persona_list = engine.list_personas()
    persona_choices = [f"{p['persona_id']} | {p['name']}" for p in persona_list]

    # ── 人格详情 ──
    def show_persona_detail(persona_choice: str):
        if not persona_choice:
            return "请选择一个人格"
        pid = persona_choice.split(" | ")[0]
        persona = engine._persona_profiles.get(pid)
        if not persona:
            return f"未找到人格: {pid}"
        lines = [
            f"## {persona.name}",
            f"**ID:** {persona.persona_id}",
            f"**领域:** {persona.domain}",
            f"**描述:** {persona.description}",
            f"**风格标签:** {', '.join(persona.style_tags)}",
            "\n### 特质维度",
        ]
        for trait, val in persona.traits.items():
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            lines.append(f"- **{trait}:** [{bar}] {val:.2f}")
        return "\n".join(lines)

    # ── 图谱 ──
    def show_atlas():
        if engine.embeddings is None:
            return None, "请先训练模型"
        data = engine.get_atlas_2d()
        coords = np.array(data["coordinates"])
        labels = np.array(data["labels"])
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap='tab10', alpha=0.7, s=60)
        ax.set_title("人格分布图谱", fontsize=14)
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, label='Cluster')
        plt.tight_layout()
        path = Path("atlas_plot.png")
        fig.savefig(path, dpi=100)
        plt.close(fig)
        return str(path), f"共 {len(coords)} 个样本，{len(set(labels))} 个聚类"

    # ── Morph ──
    def fill_sliders(persona_choice: str):
        if not persona_choice:
            return 0.5, 0.5, 0.5, 0.5, 0.5
        pid = persona_choice.split(" | ")[0]
        p = engine._persona_profiles.get(pid)
        if not p:
            return 0.5, 0.5, 0.5, 0.5, 0.5
        return (
            p.traits.get("aggression", 0.5),
            p.traits.get("warmth", 0.5),
            p.traits.get("rationality", 0.5),
            p.traits.get("mystery", 0.5),
            p.traits.get("dominance", 0.5),
        )

    def morph_persona(persona_choice, aggression, warmth, rationality, mystery, dominance):
        if not persona_choice:
            return "请先选择人格", ""
        pid = persona_choice.split(" | ")[0]
        try:
            if engine.current_persona is None or engine.current_persona.persona_id != pid:
                engine.initialize_by_persona_id(pid)
            source = engine.current_persona
            adjustments = {}
            for trait, new_val in [
                ("aggression", aggression), ("warmth", warmth),
                ("rationality", rationality), ("mystery", mystery),
                ("dominance", dominance),
            ]:
                old_val = source.traits.get(trait, 0.5)
                delta = new_val - old_val
                if abs(delta) > 0.01:
                    adjustments[trait] = round(delta, 2)
            if not adjustments:
                return "无变化", show_persona_detail(persona_choice)
            morphed = engine.morph_traits(adjustments)
            result = [f"## {morphed.name}", f"**来源:** {source.name}", f"**调整:** {adjustments}", "\n### 新特质"]
            for trait, val in morphed.traits.items():
                bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
                result.append(f"- **{trait}:** [{bar}] {val:.2f}")
            return "\n".join(result), f"新人格已注册: {morphed.persona_id}"
        except Exception as e:
            return f"错误: {e}", ""

    # ── 对话（带 LLM 降级） ──
    def chat_with_persona(persona_choice: str, user_input: str, history: list):
        if not persona_choice or not user_input:
            return history or []
        if history is None:
            history = []
        pid = persona_choice.split(" | ")[0]
        try:
            if engine.current_persona is None or engine.current_persona.persona_id != pid:
                engine.initialize_by_persona_id(pid)
            response = _try_llm_chat(engine, user_input)
            if response is None:
                response = _template_chat(pid, user_input)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": f"[错误] {e}"})
        return history

    # ── 界面 ──
    with gr.Blocks(title="渊 — 人格AI系统", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧠 渊 — 人格AI系统")
        gr.Markdown(
            f"已加载 **{len(persona_list)}** 个人格档案 | {len(engine.archetypes)} 个聚类原型\n\n"
            "> 把性格变成可计算、可旋转、可克隆的东西。"
        )

        with gr.Tab("🎭 人格浏览"):
            persona_dd = gr.Dropdown(
                choices=persona_choices, label="选择人格",
                value=persona_choices[0] if persona_choices else None,
            )
            detail_md = gr.Markdown("请选择一个人格查看详情")
            persona_dd.change(show_persona_detail, inputs=[persona_dd], outputs=[detail_md])

        with gr.Tab("🔄 人格旋转 (Morph)"):
            gr.Markdown("拖动滑块调整人格维度，实时生成新变体")
            morph_persona_dd = gr.Dropdown(
                choices=persona_choices, label="种子人格",
                value=persona_choices[0] if persona_choices else None,
            )
            with gr.Row():
                s_aggression = gr.Slider(0, 1, 0.5, step=0.05, label="攻击性")
                s_warmth = gr.Slider(0, 1, 0.5, step=0.05, label="温暖度")
                s_rationality = gr.Slider(0, 1, 0.5, step=0.05, label="理性度")
            with gr.Row():
                s_mystery = gr.Slider(0, 1, 0.5, step=0.05, label="神秘感")
                s_dominance = gr.Slider(0, 1, 0.5, step=0.05, label="支配性")
            btn_morph = gr.Button("旋转生成", variant="primary")
            morph_result = gr.Markdown("调整滑块后点击生成")
            morph_status = gr.Textbox(label="状态", interactive=False)
            morph_persona_dd.change(
                fill_sliders, inputs=[morph_persona_dd],
                outputs=[s_aggression, s_warmth, s_rationality, s_mystery, s_dominance],
            )
            btn_morph.click(
                morph_persona,
                inputs=[morph_persona_dd, s_aggression, s_warmth, s_rationality, s_mystery, s_dominance],
                outputs=[morph_result, morph_status],
            )

        with gr.Tab("🗺️ 人格图谱"):
            btn_atlas = gr.Button("生成图谱")
            atlas_img = gr.Image(label="2D 人格分布")
            atlas_info = gr.Textbox(label="图谱信息", interactive=False)
            btn_atlas.click(show_atlas, outputs=[atlas_img, atlas_info])

        with gr.Tab("💬 对话"):
            gr.Markdown(
                "选择人格后输入文字对话。\n\n"
                "⚡ 本地运行（有 Ollama）→ 真实 LLM 人格对话\n"
                "🌐 在线版（无 LLM）→ 智能模板回复（基于人格风格）"
            )
            chat_persona_dd = gr.Dropdown(
                choices=persona_choices, label="对话人格",
                value=persona_choices[0] if persona_choices else None,
            )
            chatbot = gr.Chatbot(label="对话", type="messages")
            chat_state = gr.State([])
            msg = gr.Textbox(label="输入", placeholder="输入你想说的话...")

            def handle_chat(persona_choice, user_input, history):
                if not persona_choice or not user_input:
                    return (history or []), (history or [])
                if history is None:
                    history = []
                pid = persona_choice.split(" | ")[0] if " | " in persona_choice else persona_choice
                # 在线版不走 LLM，直接用模板回复
                resp = _template_chat(pid, user_input)
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": resp})
                return history, history

            msg.submit(handle_chat, inputs=[chat_persona_dd, msg, chat_state], outputs=[chatbot, chat_state])

    return demo


# ═══════════════════ 启动 ═══════════════════

if __name__ == "__main__":
    data_path = Path(__file__).parent / "data" / "full_personas.json"

    if data_path.exists():
        engine = PersonalityEngine(get_config(n_factors=10))
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        descriptions = [item["description"] for item in data["archetypes"]]
        names = [item["name"] for item in data["archetypes"]]
        parent_ids = [item.get("id", item.get("parent_id", "")) for item in data["archetypes"]]
        engine.train(descriptions, names, parent_ids)
        print(f"✅ 从 full_personas.json 训练完成（{len(descriptions)} 个样本）")
    else:
        print("⚠️ 未找到数据文件，使用内置人格")
        engine = PersonalityEngine()

    demo = create_ui(engine)
    demo.launch(server_name="0.0.0.0", server_port=7860)
