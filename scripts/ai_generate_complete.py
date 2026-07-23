"""
完整的人格数据增强脚本 - AI生成 + 合并 + 保存
将所有新对话合并到 full_personas.json
"""

import json
import requests
from pathlib import Path
import time
import sys
import os

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


def call_ai(prompt):
    try:
        resp = requests.post(f"{OLLAMA_HOST}/api/generate", json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9}
        }, timeout=60)
        
        if resp.status_code == 200:
            text = resp.json().get("response", "").strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            return json.loads(text) if text else []
        return []
    except:
        return []


def generate_dialogues(persona, scene_name, count=8):
    """生成单个场景的对话"""
    prompt = f"""请为以下人物生成{count}条符合性格的中文对话。

【人物】
名字：{persona['name']}
领域：{persona['domain']}
描述：{persona['description']}
特质：{str(persona['traits'])}
标签：{', '.join(persona.get('style_tags', []))}

【场景】{SCENE_DESCS.get(scene_name, '')}

要求：每条10-50字，完全符合人物风格，避免重复。
返回纯JSON数组格式。

开始："""
    
    return [d for d in call_ai(prompt) if isinstance(d, str) and len(d) > 3][:count]


def main():
    print("=" * 60)
    print("🧠 人格对话 AI 批量增强")
    print("=" * 60)
    
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    base = [p for p in data["archetypes"] if "_" not in p["id"]]
    
    print(f"\n基础人格：{len(base)}个")
    print(f"场景数：{len(SCENES)}")
    print(f"每场景对话：8条\n")
    
    total_new = 0
    
    for persona in base:
        print(f"\n{'='*40}")
        print(f"📝 {persona['name']}")
        print("-" * 40)
        
        for scene in SCENES:
            dialogues = generate_dialogues(persona, scene)
            
            if dialogues:
                total_new += len(dialogues)
                print(f"  ✅ {scene}: +{len(dialogues)}条")
            else:
                print(f"  ⚠️ {scene}: 失败")
            
            time.sleep(0.5)
        
        time.sleep(2)
    
    # 合并回原数据
    merged = {
        "archetypes": [],
        "metadata": {
            "enhanced_by": "AI批量生成",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_new_dialogues": total_new,
            "scenes_per_persona": SCENES,
            "count_per_scene": 8
        }
    }
    
    enhanced_map = {}
    for persona in base:
        scenes = {}
        for scene in SCENES:
            dialogues = generate_dialogues(persona, scene)
            if dialogues:
                scenes[scene] = dialogues
        enhanced_map[persona["id"]] = scenes
    
    for orig in data["archetypes"]:
        new_p = dict(orig)
        eid = orig["id"]
        
        if eid in enhanced_map:
            new_p["scene_dialogues"] = enhanced_map[eid]
            total_scene_count = sum(len(v) for v in new_p["scene_dialogues"].values())
            print(f"\n✅ {eid}: {total_scene_count}条场景对话已添加")
        
        merged["archetypes"].append(new_p)
    
    output_path = DATA_DIR / "full_personas_v3.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"🎉 完成!")
    print(f"新增对话总数: {total_new}")
    print(f"输出文件: {output_path}")
    
    # 统计
    base_count = len([a for a in merged["archetypes"] if "_" not in a["id"]])
    all_scene_count = sum(len(a.get("scene_dialogues", {})) 
                         for a in merged["archetypes"] if a.get("scene_dialogues"))
    print(f"增强后基础人格: {base_count}")
    print(f"场景对话总计: {all_scene_count}")
    print(f"档案总数: {len(merged['archetypes'])}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
