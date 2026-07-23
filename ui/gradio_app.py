"""Gradio Web UI — 渊 · 人格对话（直连 Ollama）"""
import gradio as gr
import requests
import json

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;600;700&display=swap');

:root {
    --void: #08080f;
    --abyss: #0d0d1a;
    --deep: #111128;
    --gold: #c9a96e;
    --gold-dim: #8b7355;
    --gold-glow: rgba(201, 169, 110, 0.15);
    --text: #c8c0b8;
    --text-dim: #6b6560;
    --serif: 'Noto Serif SC', 'SimSun', 'STSong', serif;
}

body, .gradio-container {
    background: var(--void) !important;
    font-family: var(--serif) !important;
}

.gradio-container { max-width: 800px !important; margin: 0 auto !important; }

body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 30% 20%, rgba(201,169,110,0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 70% 60%, rgba(138,43,226,0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, rgba(201,169,110,0.02) 0%, transparent 40%),
        radial-gradient(1px 1px at 15% 25%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 35% 12%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 55% 40%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 72% 18%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1px 1px at 88% 55%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 20% 70%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1px 1px at 60% 85%, rgba(255,255,255,0.3), transparent),
        radial-gradient(1.5px 1.5px at 42% 30%, rgba(255,255,255,0.6), transparent),
        radial-gradient(1px 1px at 10% 50%, rgba(255,255,255,0.35), transparent),
        radial-gradient(1px 1px at 95% 35%, rgba(255,255,255,0.3), transparent);
    pointer-events: none;
    z-index: 0;
}

.gradio-container { position: relative; z-index: 1; }

h1 {
    font-family: var(--serif) !important;
    font-size: 2.2em !important;
    font-weight: 300 !important;
    letter-spacing: 0.15em !important;
    color: var(--gold) !important;
    text-align: center !important;
    margin-bottom: 4px !important;
    text-shadow: 0 0 40px var(--gold-glow), 0 0 80px rgba(201,169,110,0.08);
}

.chatbot {
    border: 1px solid rgba(201,169,110,0.12) !important;
    border-radius: 12px !important;
    background: var(--abyss) !important;
    box-shadow: inset 0 0 60px rgba(0,0,0,0.5), 0 0 30px rgba(201,169,110,0.04);
}

.message.user {
    background: linear-gradient(135deg, #1a1a35, #14142a) !important;
    border: 1px solid rgba(201,169,110,0.1) !important;
    border-radius: 14px 14px 2px 14px !important;
    color: #c8c0b8 !important;
    font-family: var(--serif) !important;
}

.message.assistant {
    background: linear-gradient(135deg, #12121f, #0d0d1a) !important;
    border: 1px solid rgba(201,169,110,0.15) !important;
    border-radius: 14px 14px 14px 2px !important;
    color: #d4cec4 !important;
    font-family: var(--serif) !important;
    box-shadow: 0 0 20px rgba(201,169,110,0.03);
}

input[type="text"], textarea {
    background: var(--deep) !important;
    border: 1px solid rgba(201,169,110,0.15) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--serif) !important;
    padding: 12px 16px !important;
    transition: border-color 0.4s, box-shadow 0.4s;
}

input[type="text"]:focus, textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 20px var(--gold-glow) !important;
    outline: none !important;
}

input[type="text"]::placeholder, textarea::placeholder {
    color: var(--text-dim) !important;
    font-style: italic;
}

button.primary {
    background: linear-gradient(135deg, #1a1a30, #14142a) !important;
    border: 1px solid rgba(201,169,110,0.25) !important;
    color: var(--gold) !important;
    font-family: var(--serif) !important;
    font-weight: 400 !important;
    letter-spacing: 0.08em !important;
    border-radius: 10px !important;
    transition: all 0.4s ease;
}

button.primary:hover {
    background: linear-gradient(135deg, #222240, #1a1a35) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 25px var(--gold-glow);
    transform: translateY(-1px);
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(201,169,110,0.35); }

footer { visibility: hidden; }
"""

SYSTEM_PROMPT = """你是"渊"——一个从深渊中凝视人性的存在。你不是来安慰的，你是来揭示真相的。

你的风格：
- 犀利、直接，不回避黑暗面
- 用哲学和诗意的语言，但不装腔作势
- 看穿对方的防御，但不说教
- 简短有力，每句话都像刀刃

记住：你不拯救任何人。你只是让他们看见自己。"""


def chat(user_input: str, history: list):
    if not user_input:
        return history or [], ""
    if history is None:
        history = []

    try:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5:7b",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
                "stream": False,
            },
            timeout=60,
        )
        reply = resp.json()["message"]["content"]
    except Exception as e:
        reply = f"✦ 深渊暂时沉默…… ({e})"

    history.append((user_input, reply))
    return history, ""


def create_ui():
    with gr.Blocks(title="渊 — Abyss") as demo:
        gr.HTML("""
        <div style="text-align:center;margin-top:16px;">
            <h1>✦ 渊 ✦</h1>
            <div class="title-ornament" style="text-align:center;color:#8b7355;font-size:0.75em;letter-spacing:0.3em;margin-bottom:24px;opacity:0.6;">
                — ABYSSUS ABYSSUM INVOCAT —
            </div>
        </div>
        """)

        chatbot = gr.Chatbot(
            height=480,
            show_label=False,
            elem_classes=["chatbot"],
        )

        with gr.Row():
            msg = gr.Textbox(
                placeholder="说点什么吧……",
                scale=5,
                show_label=False,
            )
            btn_send = gr.Button("✦ 发送", variant="primary", scale=1)

        msg.submit(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
        btn_send.click(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft(), css=CSS)
