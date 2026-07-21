"""CLI — python -m personality_core"""
import sys
import json
from pathlib import Path


def _get_engine():
    """懒加载引擎：从预训练模型或数据训练"""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
    from personality_core.engine import PersonalityEngine
    from personality_core.config import get_config

    PROJECT = Path(__file__).resolve().parent.parent.parent
    model_path = PROJECT / "models" / "personality_model"

    if model_path.with_suffix(".meta.json").exists():
        return PersonalityEngine.load_model(str(model_path))

    data_path = PROJECT / "data" / "archetypes_extended.json"
    if data_path.exists():
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
        engine = PersonalityEngine(get_config(n_factors=5))
        engine.train(
            [d["description"] for d in data["archetypes"]],
            [d["name"] for d in data["archetypes"]],
            [d.get("parent_id", "") for d in data["archetypes"]],
        )
        return engine

    return PersonalityEngine(get_config(n_factors=5))


def cmd_list(args):
    """列出所有人格"""
    engine = _get_engine()
    personas = engine.list_personas()
    for p in personas:
        traits = p["traits"]
        t_str = " ".join(f"{k}={v:.0%}" for k, v in traits.items())
        print(f"  {p['persona_id']:20s} {p['name']:12s} {t_str}")


def cmd_chat(args):
    """启动对话"""
    engine = _get_engine()
    persona_id = args.persona or "yuan"

    try:
        engine.initialize_by_persona_id(persona_id)
    except ValueError:
        print(f"人格 '{persona_id}' 不存在，可用: {[p['persona_id'] for p in engine.list_personas()]}")
        return

    print(f"🧠 {engine.current_persona.name} 已激活。输入内容开始对话，/quit 退出。")
    print()

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit"):
            print("再见。")
            break
        if user_input.startswith("/persona "):
            new_id = user_input.split(" ", 1)[1].strip()
            try:
                engine.initialize_by_persona_id(new_id)
                print(f"   → 切换到: {engine.current_persona.name}")
            except ValueError:
                print(f"   ❌ 人格 '{new_id}' 不存在")
            continue

        resp = engine.chat(user_input)
        print(f"{engine.current_persona.name}: {resp}")
        print()


def cmd_export(args):
    """导出人格"""
    engine = _get_engine()
    persona_id = args.persona or "yuan"
    path = args.output or f"{persona_id}.persona.json"
    try:
        engine.export_persona(persona_id, path)
        print(f"✅ 已导出到 {path}")
    except ValueError as e:
        print(f"❌ {e}")


def cmd_import(args):
    """导入人格"""
    engine = _get_engine()
    path = args.file
    try:
        persona = engine.import_persona(path)
        print(f"✅ 已导入: {persona.persona_id} ({persona.name})")
    except Exception as e:
        print(f"❌ 导入失败: {e}")


def cmd_predict(args):
    """预测文本的 trait"""
    engine = _get_engine()
    text = args.text
    traits = engine.predict_traits(text)
    for k, v in traits.items():
        bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
        print(f"  {k:15s} {bar} {v:.0%}")


def cmd_matrix(args):
    """人格相似度矩阵"""
    engine = _get_engine()
    result = engine.matrix_compare()

    # 标题行
    names = result["persona_names"]
    max_name = max(len(n) for n in names)
    header = " " * (max_name + 2) + "".join(f"{n:>8s}" for n in names)
    print(header)

    pids = result["persona_ids"]
    n = len(pids)
    # 构建全矩阵
    sim_map = {}
    for pair in result["pairs"]:
        sim_map[(pair["a"], pair["b"])] = pair["similarity"]
        sim_map[(pair["b"], pair["a"])] = pair["similarity"]

    for i in range(n):
        row = f"{names[i]:<{max_name+2}s}"
        for j in range(n):
            if i == j:
                row += "    1.00"
            else:
                sim = sim_map.get((pids[i], pids[j]), 0.5)
                row += f"  {sim:.2f}"
        print(row)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="personality-core",
        description="人格AI系统 CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="列出所有人格")

    # chat
    p_chat = sub.add_parser("chat", help="启动对话")
    p_chat.add_argument("--persona", "-p", default="yuan", help="人格ID (默认: yuan)")

    # export
    p_export = sub.add_parser("export", help="导出人格")
    p_export.add_argument("--persona", "-p", default="yuan", help="人格ID")
    p_export.add_argument("--output", "-o", help="输出文件路径")

    # import
    p_import = sub.add_parser("import", help="导入人格")
    p_import.add_argument("file", help=".persona.json 文件路径")

    # predict
    p_pred = sub.add_parser("predict", help="预测文本的trait")
    p_pred.add_argument("text", help="人格描述文本")

    # matrix
    sub.add_parser("matrix", help="人格相似度矩阵")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "chat": cmd_chat,
        "export": cmd_export,
        "import": cmd_import,
        "predict": cmd_predict,
        "matrix": cmd_matrix,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
