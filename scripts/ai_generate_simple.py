"""
AI 批量生成对话样本 - 简化版
直接为每个基础人格生成5个场景×8条对话
"""

import json
import requests
from pathlib import Path
import time
import sys
import os

# 强制 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"
DATA_DIR = Path(__file__).parent.parent / "data"

SCENES = ["日常闲聊", "情感安慰", "尖锐辩论", "哲学思考", "神秘预言"]
SCENE_DESCS = {
    "日常闲聊": "轻松、自然、带点人格特色的日常对话",
    "情感安慰": "支持性语言，体现共情与理解",
    "尖锐辩论": "挑战用户观点，激发深度思考",
    "哲学思考": "抽象概念，人生意义，存在主义探讨",
    "神秘预言": "模糊但引人深思的表达，带有启示性"
}


def call_ai(prompt, max_tokens=2000):
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9}
        }, timeout=60)
        
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
        else:
            print(f"❌ API error: {resp.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def generate_for_person(persona, count=8):
    """为一个场景生成对话"""
    prompt = f"""请为这个人物生成{count}条符合性格的中文对话。

名字：{persona['name']}
领域：{persona['domain']}
描述：{persona['description']}
特质：{str(persona['traits'])}
标签：{', '.join(persona.get('style_tags', []))}

场景：{SCENE_DESCS.get(persona['scene_name'], '')}

要求：
- 完全符合人物说话风格
- 避免重复
- 每条10-50字
- 返回纯 JSON 数组，如 ["句子1", "句子2", ...]

开始："""
    
    dialogues = call_ai(prompt)
    return [d for d in dialogues if isinstance(d, str) and len(d) > 3][:count]


def main():
    print("=" * 60)
    print("🚀 AI 批量生成人格对话")
    print("=" * 60)
    
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    base = [p for p in data["archetypes"] if "_" not in p["id"]]
    
    print(f"\n基础人格数: {len(base)}")
    print(f"每场景生成: 8条")
    print(f"总场景数: {len(SCENES)}")
    print(f"预计新增: {len(base) * len(SCENES) * 8} 条\n")
    
    total_new = 0
    
    for persona in base:
        print(f"\n📝 处理：{persona['name']}")
        print("-" * 40)
        
        for scene_name in SCENES:
            # 调用 AI 生成
            dialogues = generate_for_person({
                **persona,
                "scene_name": scene_name
            }, count=8)
            
            if dialogues:
                total_new += len(dialogues)
                print(f"  ✅ {scene_name}: +{len(dialogues)}条")
            else:
                print(f"  ⚠️ {scene_name}: 失败")
            
            time.sleep(1)  # 避免过快
        
        time.sleep(2)  # 人物之间暂停
    
    print(f"\n{'='*60}")
    print(f"✅ 完成！新增 {total_new} 条对话")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
