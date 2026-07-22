"""Gradio Web UI — 人格可视化、旋转与交互"""
import sys
from pathlib import Path

_src = Path(__file__).parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from personality_core.engine import PersonalityEngine


# 全局配色
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_ui(engine: PersonalityEngine):
    """创建完整 Gradio 界面"""

    # ── 人格选择器 ──
    persona_list = engine.list_personas()
    persona_choices = [f"{p['persona_id']} | {p['name']}" for p in persona_list]
    persona_ids = [p['persona_id'] for p in persona_list]

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

    # ── Morph 面板 ──
    def morph_persona(persona_choice: str, aggression: float, warmth: float,
                      rationality: float, mystery: float, dominance: float):
        if not persona_choice:
            return "请先选择人格", ""
        pid = persona_choice.split(" | ")[0]
        try:
            if engine.current_persona is None or engine.current_persona.persona_id != pid:
                engine.initialize_by_persona_id(pid)
            source = engine.current_persona
            adjustments = {}
            for trait, new_val in [("aggression", aggression), ("warmth", warmth),
                                     ("rationality", rationality), ("mystery", mystery),
                                     ("dominance", dominance)]:
                old_val = source.traits.get(trait, 0.5)
                delta = new_val - old_val
                if abs(delta) > 0.01:
                    adjustments[trait] = round(delta, 2)
            if not adjustments:
                return "无变化", show_persona_detail(persona_choice)
            morphed = engine.morph_traits(adjustments)
            result = [
                f"## {morphed.name}",
                f"**来源:** {source.name}",
                f"**调整:** {adjustments}",
                "\n### 新特质",
            ]
            for trait, val in morphed.traits.items():
                bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
                result.append(f"- **{trait}:** [{bar}] {val:.2f}")
            return "\n".join(result), f"新人格已注册: {morphed.persona_id}"
        except Exception as e:
            return f"错误: {e}", ""

    # ── 聊天 ──
    def chat_with_persona(persona_choice: str, user_input: str, history: list):
        if not persona_choice or not user_input:
            return history
        pid = persona_choice.split(" | ")[0]
        try:
            if engine.current_persona is None or engine.current_persona.persona_id != pid:
                engine.initialize_by_persona_id(pid)
            response = engine.chat(user_input)
            history.append((user_input, response))
        except Exception as e:
            history.append((user_input, f"[错误] {e}"))
        return history

    # ── 构建界面 ──
    with gr.Blocks(title="Personality Core — 人格AI系统", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧠 Personality Core — 人格AI系统")
        gr.Markdown(f"已加载 **{len(persona_list)}** 个人格档案 | {len(engine.archetypes)} 个聚类原型")

        with gr.Tab("🎭 人格浏览"):
            with gr.Row():
                persona_dd = gr.Dropdown(
                    choices=persona_choices,
                    label="选择人格",
                    value=persona_choices[0] if persona_choices else None,
                )
            detail_md = gr.Markdown("请选择一个人格查看详情")
            persona_dd.change(show_persona_detail, inputs=[persona_dd], outputs=[detail_md])

        with gr.Tab("🔄 人格旋转 (Morph)"):
            gr.Markdown("拖动滑块调整人格维度，实时生成新变体")
            with gr.Row():
                morph_persona_dd = gr.Dropdown(
                    choices=persona_choices,
                    label="种子人格",
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

            # 选择人格时自动回填滑块
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

            morph_persona_dd.change(
                fill_sliders,
                inputs=[morph_persona_dd],
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

        with gr.Tab("💬 对话测试"):
            gr.Markdown("选择人格后输入文字，测试 LLM 对话（需 Ollama）")
            chat_persona_dd = gr.Dropdown(
                choices=persona_choices,
                label="对话人格",
                value=persona_choices[0] if persona_choices else None,
            )
            chatbot = gr.Chatbot(label="对话")
            msg = gr.Textbox(label="输入", placeholder="输入你想说的话...")
            msg.submit(
                chat_with_persona,
                inputs=[chat_persona_dd, msg, chatbot],
                outputs=[chatbot],
            )

    return demo


if __name__ == "__main__":
    import json

    data_path = Path(__file__).parent.parent / "data" / "full_personas.json"

    if data_path.exists():
        from personality_core.config import get_config
        engine = PersonalityEngine(get_config(n_factors=10))
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        descriptions = [item["description"] for item in data["archetypes"]]
        names = [item["name"] for item in data["archetypes"]]
        parent_ids = [item.get("id", item.get("parent_id", "")) for item in data["archetypes"]]
        engine.train(descriptions, names, parent_ids)
        print(f"从 full_personas.json 训练引擎（{len(descriptions)} 样本）")
    else:
        print("未找到数据文件，启动空引擎")
        engine = PersonalityEngine()

    demo = create_ui(engine)
    demo.launch(server_name="0.0.0.0", server_port=7860)
