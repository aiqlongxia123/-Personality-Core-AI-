"""scripts/activate_yuan.py — 激活渊人格的最小入口 (Persona Switching skill)

用法::

    python scripts/activate_yuan.py                # 进 REPL, 默认激活渊
    python scripts/activate_yuan.py --persona baozao_niangmen
    python scripts/activate_yuan.py --no-activate  # 仅挂载调参, 不立即激活

设计要点:
    1. 自动 import 并实例化 PersonalityEngine
    2. 调用 attach_tuner 挂载单目标调参
    3. 默认 activate_now=True, 优先按 persona_id 激活 (避开聚类索引依赖)
    4. 若用户输入含软化情绪词, route_by_tone() 会推荐人格, 但不强制切换
       (切换动作不向用户展示, 保持对话自然)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser(description="激活渊人格 + 挂载调参")
    parser.add_argument(
        "--persona", "-p", default="yuan",
        help="默认激活的人格 id (默认 yuan)",
    )
    parser.add_argument(
        "--no-activate", action="store_true",
        help="只挂载 attach_tuner, 不激活人格 (供 train 前的中间态使用)",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="单次对话 (读取 stdin/参数), 不进 REPL",
    )
    parser.add_argument(
        "--text", "-t", default=None,
        help="配合 --once 使用, 直接喂一句话",
    )
    args = parser.parse_args()

    # ── 延迟导入, 路径已就绪 ──
    from personality_core.engine import PersonalityEngine
    from personality_core.engine_tuner import attach_tuner, route_by_tone

    engine = PersonalityEngine()

    # ── 试一下 train, 没有数据就跳过 (activate_now=False 也能挂 tuner) ──
    data_path = PROJECT / "data" / "archetypes_extended.json"
    if data_path.exists():
        import json
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
        try:
            engine.train(
                [d["description"] for d in data["archetypes"]],
                [d["name"] for d in data["archetypes"]],
                [d.get("parent_id", "") for d in data["archetypes"]],
            )
        except Exception as exc:  # 仅记录, 不退出
            print(f"[warn] train 失败: {exc}")

    # ── 挂载 tuner + 可选激活 ──
    attach_tuner(engine, default_persona_id=args.persona, activate_now=not args.no_activate)

    if not args.no_activate:
        print(f"[OK] {engine.current_persona.name if engine.current_persona else '?'} 已就位")

    # ── 验证挂载 ──
    assert callable(getattr(engine, "tune_hyperparameters", None)), "tune_hyperparameters 未挂载"
    assert callable(getattr(engine, "route_by_tone", None)), "route_by_tone 未挂载"
    print("[OK] tune_hyperparameters / route_by_tone 已挂载")

    # ── 单次对话 ──
    if args.once:
        text = args.text or (input("你: ").strip() if sys.stdin.isatty() else "")
        if text:
            suggested = route_by_tone(text)
            if suggested:
                # 仅打印到 stderr, 主流程不 echo (Persona Switching 约定)
                print(f"[tone → {suggested}]", file=sys.stderr)
            print(engine.chat(text))
        return

    # ── REPL (隐藏切换痕迹) ──
    print("输入内容开始对话, /quit 退出, /persona <id> 切换.")
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit"):
            print("再见.")
            break
        if user_input.startswith("/persona "):
            new_id = user_input.split(" ", 1)[1].strip()
            try:
                engine.initialize_by_persona_id(new_id)
                # 切换动作不 echo, 保持对话自然
            except Exception as exc:
                print(f"❌ {exc}")
            continue
        suggested = route_by_tone(user_input)
        if suggested:
            print(f"[tone → {suggested}]", file=sys.stderr)
        print(f"{engine.current_persona.name}: {engine.chat(user_input)}")
        print()


if __name__ == "__main__":
    main()
