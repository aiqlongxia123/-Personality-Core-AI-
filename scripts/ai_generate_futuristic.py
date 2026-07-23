"""
生成更多科幻/未来/预言方向的人格档案
用 Ollama AI 批量创建 15-20 个新领域人格
"""

import json
import requests
from pathlib import Path
import time
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

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


def build_prompt(batch_num):
    return f"""请为以下科幻/未来/预言方向生成 {batch_num} 个高质量人格档案。

要求：
- 每个档案包含：id, name, domain, description, traits, style_tags, morph_directions, sample_dialogue(5条)
- domain 必须包含 futuristic / prophecy / technology / cyberpunk / posthuman / science-fiction 等
- description 至少 80 字，要有深度和画面感
- traits 为 0-1 浮点数（aggression/warmth/mystery/rationality/dominance）
- sample_dialogue 是中文，完全符合该人物说话风格
- 返回纯 JSON 数组格式

## 输出格式示例
[
  {{
    "id": "unique_id",
    "name": "中文名",
    "domain": "futuristic",
    "description": "描述...",
    "traits": {{"aggression": 0.6, "warmth": 0.3, "mystery": 0.9, "rationality": 0.7, "dominance": 0.5}},
    "style_tags": ["神秘", "未来", "预言"],
    "morph_directions": {{
      "更温和": {{"factor_shift": [-0.3, 0.2, -0.1, 0, -0.2], "weight": 0.5}}
    }},
    "sample_dialogue": [
      "第一句对话",
      "第二句对话",
      "第三句对话"
    ]
  }}
]

## 要求
- 每个人物要有独特的世界观和说话风格
- 涉及时间、空间、意识、机械、进化、数字永生、预言等主题
- 场景要多样化：日常、安慰、辩论、哲学、预言
- 返回 {batch_num} 个档案

开始："""


def main():
    print("=" * 60)
    print("🧬 AI 生成科幻/未来/预言方向人格")
    print("=" * 60)
    
    # 加载当前数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_ids = {a["id"] for a in data["archetypes"]}
    
    all_new = []
    
    for batch in range(2):  # 分2批，每批约 10 个
        print(f"\n🔄 第 {batch+1} 批生成...")
        
        response = call_ollama(build_prompt(10))
        
        if isinstance(response, list):
            valid = [p for p in response if isinstance(p, dict) and "id" in p]
            
            for p in valid:
                if p["id"] not in existing_ids:
                    all_new.append(p)
                    existing_ids.add(p["id"])
            
            print(f"  ✅ +{len(valid)} 个人格")
        else:
            print(f"  ⚠️ 无有效数据")
        
        time.sleep(2)
    
    if all_new:
        data["archetypes"].extend(all_new)
        
        output_path = DATA_DIR / "full_personas_v4_ai_generated.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 完成! 新增 {len(all_new)} 个新人格")
        print(f"总计档案: {len(data['archetypes'])}")
        print(f"输出: {output_path}")
        
        # 统计领域
        domains = {}
        for p in all_new:
            d = p.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        print(f"领域分布: {domains}")
    else:
        print("⚠️ 未生成新人物")


if __name__ == "__main__":
    main()
