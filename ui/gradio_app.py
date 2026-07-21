"""Gradio Web UI — 人格可视化与交互"""
import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from personality_core.engine import PersonalityEngine


def create_ui(engine: PersonalityEngine):
    """创建Gradio界面"""

    def show_archetypes():
        if not engine.archetypes:
            return "请先训练模型"
        lines = ["### 人格原型列表\n"]
        for a in engine.archetypes:
            lines.append(f"**{a['name']}** — 成员数: {a['size']}")
        return "\n".join(lines)

    def show_atlas():
        if engine.embeddings is None:
            return "请先训练模型"
        data = engine.get_atlas_2d()
        coords = np.array(data["coordinates"])
        labels = np.array(data["labels"])

        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap='tab10', alpha=0.7)
        ax.set_title("人格分布图谱 (UMAP/PCA)")
        ax.set_xlabel("维度 1")
        ax.set_ylabel("维度 2")
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, label='Cluster')
        plt.tight_layout()

        path = "/tmp/atlas_plot.png"
        fig.savefig(path, dpi=100)
        plt.close(fig)
        return path

    def show_factors():
        factors = engine.ica.get_factor_labels()
        lines = []
        for f in factors:
            lines.append(f"**{f['factor_index']} {f['name_zh']}** ({f['name_en']})")
            lines.append(f"   Pole A: {f['pole_a']} | Pole B: {f['pole_b']}")
            lines.append("")
        return "\n".join(lines)

    def interact_demo(user_input, archetype_idx):
        if engine.emotion_core is None:
            engine.initialize_agent(int(archetype_idx))
        result = engine.interact(user_input)
        return (
            f"情绪: {result['mood']:.2f}\n"
            f"关系阶段: {result['relationship_stage']}\n"
            f"亲密度: {result['relationship_score']:.2f}"
        )

    with gr.Blocks(title="人格AI系统 v0.1") as demo:
        gr.Markdown("# 🧠 人格AI系统 — Personality Core")
        gr.Markdown("基于向量嵌入空间的人格分析、旋转与交互系统")

        with gr.Tab("人格原型"):
            gr.Markdown("## 已训练的人格原型")
            btn_show = gr.Button("显示原型列表")
            txt_archetypes = gr.Textbox(label="原型列表", lines=10)
            btn_show.click(show_archetypes, outputs=txt_archetypes)

        with gr.Tab("图谱"):
            btn_map = gr.Button("生成人格分布图")
            img_map = gr.Image(label="2D人格图谱")
            btn_map.click(show_atlas, outputs=img_map)

        with gr.Tab("因子"):
            txt_factors = gr.Textbox(label="人格因子说明", lines=15, interactive=False)
            btn_factors = gr.Button("加载因子信息")
            btn_factors.click(show_factors, outputs=txt_factors)

        with gr.Tab("交互"):
            inp = gr.Textbox(label="用户输入", placeholder="输入你想对「渊」说的话...")
            sel = gr.Slider(0, max(0, len(engine.archetypes)-1), value=0, step=1, label="选择人格原型")
            btn_interact = gr.Button("发送")
            out = gr.Textbox(label="系统状态", lines=5)
            btn_interact.click(interact_demo, inputs=[inp, sel], outputs=out)

    return demo


if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data" / "archetypes_extended.json"
    model_path = Path(__file__).parent.parent / "models" / "personality_model.json"
    src_path = Path(__file__).parent.parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # 尝试加载已训练的模型，否则从数据训练
    try:
        if model_path.exists():
            engine = PersonalityEngine()
            engine = PersonalityEngine.load_model(str(model_path))
            print(f"已加载预训练模型: {model_path}")
        elif data_path.exists():
            from personality_core.config import get_config
            engine = PersonalityEngine(get_config(n_factors=5))
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            descriptions = [item["description"] for item in data["archetypes"]]
            names = [item["name"] for item in data["archetypes"]]
            parent_ids = [item.get("parent_id", "") for item in data["archetypes"]]
            engine.train(descriptions, names, parent_ids)
            print("已从数据训练引擎")
        else:
            print("未找到数据文件，启动空引擎")
            engine = PersonalityEngine()
    except Exception as e:
        print(f"初始化失败: {e}")
        raise

    demo = create_ui(engine)
    demo.launch(server_name="0.0.0.0", server_port=7860)
