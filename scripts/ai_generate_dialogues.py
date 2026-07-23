"""
修复版：批量生成对话样本
处理 scene_dialogues 可能为 list 或 dict
"""

import json
import requests
from pathlib import Path
import time
from typing import Optional

# ==================== 配置 ====================

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"
DATA_DIR = Path(__file__).parent.parent / "data"

SCENES = [
    "日常闲聊",
    "情感安慰",
    "尖锐辩论",
    "哲学思考",
    "神秘预言"
]

SCENE_DESCRIPTIONS = {
    "日常闲聊": "轻松、自然、带点人格特色的日常对话",
    "情感安慰": "支持性语言，体现共情与理解",
    "尖锐辩论": "挑战用户观点，激发深度思考",
    "哲学思考": "抽象概念，人生意义，存在主义探讨",
    "神秘预言": "模糊但引人深思的表达，带有启示性"
}

DIALOGUE_GENERATION_PROMPT = """你是一个 AI 写作助手。请为以下人物生成符合其性格、背景的对话样本。

## 人物信息
- 名字：{name}
- 领域：{domain}
- 描述：{description}
- 性格特质：{traits}
- 风格标签：{style_tags}

## 当前场景
场景名称：{scene_name}
场景说明：{scene_desc}

## 要求
请生成 {count} 条对话，每条对话：
1. 完全符合该人物的说话风格和思维方式
2. 体现场景主题
3. 避免重复和模板化
4. 长度适中，10-50字之间
5. 用中文表达
6. 返回纯 JSON 数组格式

## 输出格式
```json
["第1句对话", "第2句对话", ...]
```

## 开始生成"""


def call_ollama(prompt: str, max_tokens: int = 2000) -> Optional[str]:
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9}
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"❌ API 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def parse_json_response(text: str) -> list:
    try:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        result = json.loads(text)
        if isinstance(result, list):
            return result
        return []
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end >= 0:
            try:
                return json.loads(text[start:end+1])
            except:
                pass
        return []


def batch_generate():
    print("=" * 60)
    print("人格对话大规模增强 - AI 批量生成")
    print("=" * 60)
    
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    base_personas = [p for p in data["archetypes"] if "_" not in p["id"]]
    total_generated = 0
    
    for persona in base_personas:
        print(f"\n{'='*40}")
        print(f"处理：{persona['name']}")
        print(f"{'='*40}")
        
        # 获取当前 scene_dialogues
        current_scenes = persona.get("scene_dialogues", {})
        
        new_dialogues = {}
        
        for scene_name in SCENES:
            existing_count = len(current_scenes.get(scene_name, []))
            needed = 10 - existing_count
            
            if needed <= 0:
                continue
            
            prompt = DIALOGUE_GENERATION_PROMPT.format(
                name=persona["name"],
                domain=persona["domain"],
                description=persona["description"],
                traits=str(persona["traits"]),
                style_tags=", ".join(persona.get("style_tags", [])),
                scene_name=scene_name,
                scene_desc=SCENE_DESCRIPTIONS.get(scene_name, ""),
                count=needed
            )
            
            print(f"  🔄 {scene_name} ({needed}条)...")
            
            for attempt in range(3):
                response = call_ollama(prompt)
                if response:
                    dialogues = parse_json_response(response)
                    if len(dialogues) >= 3:
                        new_dialogues.setdefault(scene_name, []).extend(dialogues[:needed])
                        total_generated += len(dialogues[:needed])
                        print(f"    ✅ +{len(dialogues[:needed])}")
                        break
                    else:
                        print(f"    ⚠️ 只返回{len(dialogues)}条，重试...")
                        time.sleep(1)
        
        # 更新数据
        for i, orig in enumerate(data["archetypes"]):
            if orig["id"] == persona["id"]:
                merged = dict(current_scenes)
                for scene_name, dialogues in new_dialogues.items():
                    existing = current_scenes.get(scene_name, [])
                    existing.extend(dialogues)
                    merged[scene_name] = existing[:10]
                
                data["archetypes"][i]["scene_dialogues"] = merged
                break
        
        print(f"\n✅ {persona['name']} 本轮新增 {sum(len(v) for v in new_dialogues.values())} 条对话")
        time.sleep(2)
    
    # 保存
    output_path = DATA_DIR / "full_personas_enhanced_v3.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"🎉 完成!")
    print(f"总新增对话数: {total_generated}")
    print(f"输出文件: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    import sys
    if getattr(sys.stdout, 'encoding', None) != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    batch_generate()
