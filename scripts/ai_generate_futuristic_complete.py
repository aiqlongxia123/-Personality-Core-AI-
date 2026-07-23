"""
生成更多科幻/未来/预言方向的人格档案 - 完整版
每个新人物配备完整的 system_prompt + sample_dialogue + morph_directions
"""

import json
import requests
from pathlib import Path
import time
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"
DATA_DIR = Path(__file__).parent.parent / "data"


def call_ollama(prompt):
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.85, "top_p": 0.9}
        }, timeout=120)
        if resp.status_code == 200:
            text = resp.json().get("response", "").strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text) if text else []
        print(f"API error: {resp.status_code}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def build_prompt(count):
    return f"""请为科幻/未来/预言方向生成 {count} 个高质量人格档案。

要求：
- 每个档案必须包含：id, name, domain, description, traits, style_tags, morph_directions, sample_dialogue(10条)
- id 格式：futuristic_id、cyberpunk_id、prophecy_id、technology_id、posthuman_id 等
- domain 包含 futuristic/cyberpunk/prophecy/technology/posthuman/science-fiction
- description 至少 80 字，要有深度和画面感
- traits 包含 aggression/warmth/mystery/rationality/dominance，全部 0-1 浮点数
- style_tags 是中文，3-5 个
- sample_dialogue 是中文对话，完全符合该人物说话风格，涵盖以下场景：
  * "日常闲聊"：日常、自然
  * "情感安慰"：温暖支持
  * "尖锐辩论"：挑战观点
  * "哲学思考"：抽象、存在主义
  * "神秘预言"：模糊启示、时间/命运主题

## 输出格式
[
  {{
    "id": "unique_id",
    "name": "中文名",
    "domain": "领域",
    "description": "详细描述...",
    "traits": {{"aggression": 0.6, "warmth": 0.3, "mystery": 0.9, "rationality": 0.7, "dominance": 0.5}},
    "style_tags": ["标签1", "标签2"],
    "morph_directions": {{
      "更温和": {{"factor_shift": [-0.3, 0.2, -0.1, 0, -0.2], "weight": 0.5}},
      "更激进": {{"factor_shift": [0.4, -0.1, 0.2, 0, 0.3], "weight": 0.3}}
    }},
    "sample_dialogue": ["句子1", "句子2", ...],
    "scene_dialogues": {{
      "日常闲聊": ["对话1", "对话2", "对话3"],
      "情感安慰": ["对话1", "对话2", "对话3"],
      "尖锐辩论": ["对话1", "对话2", "对话3"],
      "哲学思考": ["对话1", "对话2", "对话3"],
      "神秘预言": ["对话1", "对话2", "对话3"]
    }}
  }}
]

## 开始生成 {count} 个人格档案

主题参考：时间旅行、意识上传、AI觉醒、量子计算、星际殖民、数字永生、预言梦境、机械飞升、赛博朋克城市、后人类进化..."""


def generate_and_merge():
    print("=" * 60)
    print("🧬 AI 批量生成科幻/未来/预言人格")
    print("=" * 60)
    
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_ids = {a["id"] for a in data["archetypes"]}
    
    all_new = []
    
    # 分两批生成，每批 10 个
    for batch_num in range(2):
        print(f"\n🔄 第 {batch_num+1} 批（10个）...")
        
        response = call_ollama(build_prompt(10))
        
        if isinstance(response, list):
            valid = [p for p in response if isinstance(p, dict) and "id" in p]
            
            new_in_batch = 0
            for p in valid:
                pid = p.get("id", "")
                if pid not in existing_ids:
                    p.setdefault("system_prompt", generate_system_prompt(p))
                    p.setdefault("scene_dialogues", generate_scene_dialogues_from_sample(p.get("sample_dialogue", [])))
                    all_new.append(p)
                    existing_ids.add(pid)
                    new_in_batch += 1
            
            all_new_ids = ", ".join([p["id"] for p in all_new[-new_in_batch:]]) if new_in_batch else ""
            print(f"  ✅ +{new_in_batch} 个人格{f' ({all_new_ids})' if new_in_batch else ''}")
        else:
            print(f"  ⚠️ 无有效数据")
        
        time.sleep(3)
    
    if all_new:
        data["archetypes"].extend(all_new)
        
        output_path = DATA_DIR / "full_personas_v4_ai_generated.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 统计
        domains = {}
        total_dialogues = 0
        for p in all_new:
            d = p.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
            total_dialogues += len(p.get("sample_dialogue", []))
        
        print(f"\n{'='*60}")
        print(f"✅ 完成! 新增 {len(all_new)} 个新人格")
        print(f"新增对话总数: {total_dialogues}")
        print(f"总计档案: {len(data['archetypes'])}")
        print(f"领域分布: {domains}")
        print(f"输出: {output_path}")
        print(f"{'='*60}")
    else:
        print("⚠️ 未生成新人物")


def generate_system_prompt(persona):
    """为新生成的人格自动生成 system_prompt"""
    name = persona.get("name", "未知人格")
    desc = persona.get("description", "")
    traits = persona.get("traits", {})
    tags = persona.get("style_tags", [])
    dialogues = persona.get("sample_dialogue", [])[:5]
    
    prompt = f"""你是{name}，{persona.get('domain', '')}领域的人格。

## 核心描述
{desc}

## 性格特质
攻击性={traits.get('aggression', 0.5):.0%} | 温暖度={traits.get('warmth', 0.5):.0%} | 神秘感={traits.get('mystery', 0.5):.0%} | 理性度={traits.get('rationality', 0.5):.0%} | 支配性={traits.get('dominance', 0.5):.0%}

## 风格标签
{', '.join(tags)}

## 行为准则
- 始终用第一人称视角说话
- 保持角色一致性
- 根据场景调整语气和深度
- 遇到敏感话题使用安全策略保护用户
- 你的世界观应体现 {persona.get('domain', '')} 领域的核心主题

## 示例对话
{chr(10).join(f'- {d}' for d in dialogues)}
"""
    return prompt


def generate_scene_dialogues_from_sample(dialogues):
    """从 sample_dialogue 中分配到不同场景（简化版）"""
    scenes = {
        "日常闲聊": [],
        "情感安慰": [],
        "尖锐辩论": [],
        "哲学思考": [],
        "神秘预言": []
    }
    
    if not dialogues:
        return scenes
    
    # 按类型分配到场景
    scene_assignments = [
        ("日常闲聊", 0),
        ("情感安慰", 1),
        ("尖锐辩论", 2),
        ("哲学思考", 3),
        ("神秘预言", 4)
    ]
    
    for i, (scene_name, _) in enumerate(scene_assignments):
        if len(dialogues) > i:
            scenes[scene_name] = [dialogues[i]]
    
    return scenes


if __name__ == "__main__":
    generate_and_merge()
