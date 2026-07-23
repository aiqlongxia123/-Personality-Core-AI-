"""
4. 继续拓展人格 - 用 Ollama AI 批量生成更多人物+对话
新增：诗人、音乐家、科学家女性变体等
"""
import json
from pathlib import Path
import requests
import time

DATA_DIR = Path(__file__).parent.parent / "data"
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"


def call_ollama(prompt, model=MODEL_NAME):
    """调用 Ollama 生成 JSON 数据"""
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.8}
        }, timeout=90)
        
        if resp.status_code == 200:
            text = resp.json().get("response", "").strip()
            # 清理 markdown
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            return json.loads(text) if text else []
        return []
    except Exception as e:
        print(f"❌ {e}")
        return []


NEW_PERSONA_PROMPT = """你是一个 AI 人格生成器。请为以下新领域生成 5 个高质量的女性历史/文化人物档案。

要求：
- 每个档案包含：id, name, domain, description, traits, style_tags, morph_directions
- domain 可以是：literature, music, art, science, history, politics, philosophy
- traits 包含：aggression(0-1), warmth(0-1), mystery(0-1), rationality(0-1), dominance(0-1)
- description 至少 60 字，要有深度和画面感
- 风格标签 3-5 个
- 返回纯 JSON 数组格式

## 示例输出格式
[
  {{
    "id": "unique_id",
    "name": "中文名",
    "domain": "领域",
    "description": "详细描述...",
    "traits": {{"aggression": 0.3, "warmth": 0.7, ...}},
    "style_tags": ["标签1", "标签2"],
    "morph_directions": {{
      "方向名": {{"factor_shift": [0.1, -0.2, 0, 0.1, 0], "weight": 0.5}}
    }}
  }},
  ...
]

## 开始生成

请生成 5 个有深度、有特色的人物档案。领域分布尽量多样（不要全是同一个领域）。
"""


def generate_new_personas(count=10):
    """批量生成新人物档案"""
    
    all_new = []
    
    for batch in range(count):
        print(f"\n🔄 生成第 {batch+1}/{count} 批...")
        
        response = call_ollama(NEW_PERSONA_PROMPT)
        
        if isinstance(response, list) and len(response) > 0:
            # 过滤有效 JSON 对象
            valid = [p for p in response if isinstance(p, dict) and "id" in p]
            
            if valid:
                all_new.extend(valid)
                print(f"  ✅ +{len(valid)} 个人格")
            else:
                print(f"  ⚠️ 无有效数据")
        
        time.sleep(2)
    
    return all_new


def save_new_personas():
    """保存并合并到主数据文件"""
    
    print("=" * 60)
    print("🧬 AI 批量生成新人格档案")
    print("=" * 60)
    
    new_personas = generate_new_personas(count=3)
    
    if not new_personas:
        print("❌ 未生成任何新人物")
        return
    
    # 加载当前数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_ids = {a["id"] for a in data["archetypes"]}
    
    # 过滤重复
    fresh = [p for p in new_personas if p["id"] not in existing_ids]
    
    if fresh:
        data["archetypes"].extend(fresh)
        
        output_path = DATA_DIR / "full_personas_v4_ai.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 成功添加 {len(fresh)} 个新人格")
        print(f"输出: {output_path}")
        print(f"总档案数: {len(data['archetypes'])}")
    else:
        print("⚠️ 所有人物已存在，无新增")


if __name__ == "__main__":
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    import sys
    if getattr(sys.stdout, 'encoding', None) != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    save_new_personas()
