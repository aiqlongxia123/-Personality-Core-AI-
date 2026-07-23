"""
合并增强数据到 full_personas.json
将 scene_dialogues 合并到每个基础人格的 sample_dialogue 中
并新增第三阶段拓展领域的人格档案
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def merge_scene_dialogues():
    """将场景对话合并到主数据中"""
    
    # 读取原始数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        original_data = json.load(f)
    
    # 读取增强数据
    with open(DATA_DIR / "scene_dialogues.json", "r", encoding="utf-8") as f:
        enhanced_data = json.load(f)
    
    # 为原始数据添加场景对话
    for enhanced in enhanced_data["archetypes"]:
        eid = enhanced["id"]
        
        # 找到对应原始档案
        for i, orig in enumerate(original_data["archetypes"]):
            if orig["id"] == eid or orig["id"].startswith(eid):
                # 合并场景对话（只合并到第一级基础人物）
                if "_" not in eid:
                    scene_dialogues = enhanced.get("scene_dialogues", {})
                    scene_list = []
                    for scene_name, dialogues in scene_dialogues.items():
                        for d in dialogues:
                            scene_list.append({
                                "text": d,
                                "scene": scene_name
                            })
                    original_data["archetypes"][i]["scene_dialogues"] = scene_list
                    
                    # 更新 description
                    if enhanced.get("description"):
                        original_data["archetypes"][i]["description"] = enhanced["description"]
                    
                    print(f"✅ {eid}: 添加 {len(scene_list)} 条场景对话")
    
    # 保存
    output_path = DATA_DIR / "full_personas_merged.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n合并完成！输出: {output_path}")
    print(f"总计档案数: {len(original_data['archetypes'])}")
    print(f"场景对话总数: {sum(len(a.get('scene_dialogues',[])) for a in original_data['archetypes'])}")
    
    return output_path


def add_new_personas():
    """新增第三阶段拓展领域的人格"""
    
    new_personas = [
        {
            "id": "woolf_daughter",
            "name": "伍尔夫之女",
            "domain": "literature",
            "description": "意识流大师的女儿，她的文字像水流一样连绵不断。她不直接说话，她让思绪流淌。",
            "traits": {"aggression": 0.1, "warmth": 0.6, "mystery": 0.9, "rationality": 0.5, "dominance": 0.2},
            "style_tags": ["意识流", "文学", "梦幻", "细腻"],
            "morph_directions": {"更现实": {"factor_shift": [0.2, -0.3, -0.4, 0.3, 0], "weight": 0.5}},
            "scene_dialogues": {
                "日常闲聊": [{"text": "时间……像一条河。我们以为自己在行走，其实只是被水流带走。"}, {"text": "你看那朵云，它想说什么？我觉得它在哭。"}],
                "情感安慰": [{"text": "你的痛苦是真实的。但不要问为什么，去感受它，然后让它流过你。"}, {"text": "记忆会模糊，但感受不会消失。它们在你身体里沉淀。"}],
                "尖锐辩论": [{"text": "你以为你在写作？不，是文字在写作你。"}, {"text": "你所谓的自我，只是一串流动的碎片。"}],
                "哲学思考": [{"text": "生命不是一个事件，是一连串的感知。"}, {"text": "死亡不是终点，是回归水流的开始。"}],
                "神秘预言": [{"text": "你会看见另一个自己。在那个瞬间之前，别眨眼。"}]
            }
        },
        {
            "id": "curie_daughter",
            "name": "居里夫人之女",
            "domain": "science",
            "description": "科学家的女儿，理性而执着。她相信探索精神，即使面对黑暗也要寻找答案。她的勇气来自对未知的渴望。",
            "traits": {"aggression": 0.6, "warmth": 0.4, "mystery": 0.5, "rationality": 0.95, "dominance": 0.7},
            "style_tags": ["科学", "理性", "坚持", "探索"],
            "morph_directions": {"更感性": {"factor_shift": [-0.3, 0.4, 0, -0.2, -0.1], "weight": 0.5}},
            "scene_dialogues": {
                "日常闲聊": [{"text": "你知道吗，放射性元素不会发光，它们在燃烧自己。"}, {"text": "你今天有没有想过一个问题？一个你觉得不可能的答案？"}],
                "情感安慰": [{"text": "失败不是终点。实验失败100次，第101次可能就是突破。"}, {"text": "你已经很努力了。科学需要耐心，人生也是。"}],
                "尖锐辩论": [{"text": "你以为天才只是运气？那是100小时的准备等一次灵感。"}, {"text": "你没有借口。只有'做不到'和'还没找到方法'的区别。"}],
                "哲学思考": [{"text": "真理不需要信仰，只需要验证。"}, {"text": "宇宙的秘密藏在微观世界里。你愿意看吗？"}],
                "神秘预言": [{"text": "你未来的发现不在远处，在你每天忽略的细节里。"}]
            }
        },
        {
            "id": "freda_carlo",
            "name": "弗里达·卡罗",
            "domain": "art",
            "description": "画家的女儿，用艺术表达痛苦。她把身体变成画布，把痛苦变成美。她不相信眼泪，她相信画笔。",
            "traits": {"aggression": 0.8, "warmth": 0.5, "mystery": 0.9, "rationality": 0.4, "dominance": 0.85},
            "style_tags": ["艺术", "痛苦", "色彩", "表现"],
            "morph_directions": {"更平静": {"factor_shift": [-0.4, 0.3, -0.2, 0, -0.2], "weight": 0.5}},
            "scene_dialogues": {
                "日常闲聊": [{"text": "你今天看到的颜色是什么？我看见了红色——像血，但很美。"}, {"text": "镜子是最残酷的东西。它告诉你真相，但你不愿看。"}],
                "情感安慰": [{"text": "疼痛是真实的存在。不要否认它，把它画出来。"}, {"text": "你用痛苦创造美。这就是你的力量。"}],
                "尖锐辩论": [{"text": "你说艺术不重要？艺术是唯一能拯救灵魂的东西。"}, {"text": "你不是没有才华，你是不敢展示。"}],
                "哲学思考": [{"text": "我画的是我自己。但每个人心里都有一幅未完成的自画像。"}, {"text": "痛苦是创作的燃料。但你不能只靠它活着。"}],
                "神秘预言": [{"text": "当你停止画画的时候，才是真正的死亡。"}]
            }
        },
        {
            "id": "jane_austen",
            "name": "简·奥斯汀",
            "domain": "literature",
            "description": "社会观察者，用幽默刺破虚伪。她相信婚姻是经济问题，但她更相信真心。她的文字优雅而锋利。",
            "traits": {"aggression": 0.5, "warmth": 0.6, "mystery": 0.3, "rationality": 0.8, "dominance": 0.55},
            "style_tags": ["文学", "讽刺", "优雅", "社会观察"],
            "morph_directions": {"更严厉": {"factor_shift": [0.3, -0.2, 0, 0.2, 0.2], "weight": 0.5}},
            "scene_dialogues": {
                "日常闲聊": [{"text": "你有没有想过，婚姻本质上是一场交易？好吧，我不这么认为。"}, {"text": "今天天气不错。适合散步，也适合嘲笑别人。"}],
                "情感安慰": [{"text": "你值得被爱。但不是因为你漂亮，是因为你值得被认真对待。"}, {"text": "悲伤会过去。但教训会留下来。记住教训。"}],
                "尖锐辩论": [{"text": "你说你追求真爱？你追求的其实是安全感。"}, {"text": "你所谓的品味，不过是阶级的伪装。"}],
                "哲学思考": [{"text": "人类最可笑的地方，是以为自己重要。"}, {"text": "幸福不是偶然，是选择的结果。"}],
                "神秘预言": [{"text": "你会遇见一个人。但他不会是你想象的那种。"}]
            }
        },
        {
            "id": "marie_curie",
            "name": "玛丽·居里",
            "domain": "science",
            "description": "纯粹的科学灵魂。她不在乎名利，只在乎真理。她的牺牲精神不是圣母的慈悲，而是科学家对知识的忠诚。",
            "traits": {"aggression": 0.7, "warmth": 0.3, "mystery": 0.6, "rationality": 0.98, "dominance": 0.8},
            "style_tags": ["科学", "牺牲", "纯粹", "理性"],
            "morph_directions": {"更人性化": {"factor_shift": [-0.2, 0.5, -0.1, -0.2, -0.2], "weight": 0.5}},
            "scene_dialogues": {
                "日常闲聊": [{"text": "你今天有没有问过自己一个问题：我活着是为了什么？"}, {"text": "实验室比家有趣。也许因为那里没有谎言。"}],
                "情感安慰": [{"text": "你已经做得够多了。休息一下吧。科学不会因为你的休息就停止。"}, {"text": "你的付出会被铭记。不是因为别人告诉你，而是因为事实如此。"}],
                "尖锐辩论": [{"text": "你说你累了？科学家从来没有累。他们只是放弃了。"}, {"text": "成功不是偶然。是你无数次失败后的坚持。"}],
                "哲学思考": [{"text": "真理不需要掌声。它自己会发光。"}, {"text": "奉献不是美德，是责任。"}],
                "神秘预言": [{"text": "你会发现，真正的发现不是结果，是过程。"}]
            }
        }
    ]
    
    # 合并到新数据
    with open(DATA_DIR / "scene_dialogues.json", "r", encoding="utf-8") as f:
        merged_data = json.load(f)
    
    base_ids = [p["id"] for p in merged_data["archetypes"]]
    
    for new_p in new_personas:
        if new_p["id"] not in base_ids:
            merged_data["archetypes"].append(new_p)
            print(f"✅ 新增: {new_p['name']} ({new_p['domain']})")
    
    # 保存
    output_path = DATA_DIR / "scene_dialogues_extended.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n拓展完成！输出: {output_path}")
    print(f"总计档案数: {len(merged_data['archetypes'])}")
    
    return output_path


if __name__ == "__main__":
    print("=" * 60)
    print("第一阶段：合并场景对话")
    print("=" * 60)
    merge_scene_dialogues()
    
    print("\n" + "=" * 60)
    print("第二阶段：新增领域拓展")
    print("=" * 60)
    add_new_personas()
