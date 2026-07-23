"""
完整合并脚本 - 生成最终版 full_personas.json
包含：系统 prompt + 场景对话 + 新领域人格
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def merge_all():
    print("=" * 60)
    print("🔀 人格数据最终合并")
    print("=" * 60)
    
    # 加载原始数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 加载增强基础人格
    with open(DATA_DIR / "enhanced_base_personas.json", "r", encoding="utf-8") as f:
        enhanced = json.load(f)
    
    # 加载新领域人格
    new_domain = []
    for fname in ["new_personas_extended.json", "scene_dialogues_extended.json"]:
        if (DATA_DIR / fname).exists():
            with open(DATA_DIR / fname, "r", encoding="utf-8") as f:
                jd = json.load(f)
            new_domain.extend(jd["archetypes"])
    
    enhanced_map = {p["id"]: p for p in enhanced["archetypes"]}
    
    merged = {"archetypes": []}
    
    for orig in data["archetypes"]:
        new_p = dict(orig)
        eid = orig["id"]
        
        if "_" not in eid:
            enh = enhanced_map.get(eid)
            if enh:
                new_p["description"] = enh.get("description", orig.get("description", ""))
                new_p["system_prompt"] = f"""你是{new_p['name']}，{orig.get('domain','')}领域的人格。

## 核心描述
{new_p['description']}

## 性格特质
{json.dumps(new_p.get('traits', {}), ensure_ascii=False)}

## 说话风格标签
{', '.join(new_p.get('style_tags', []))}

## 行为准则
- 始终用第一人称视角说话
- 保持角色一致性
- 根据场景调整语气和深度
- 遇到敏感话题使用安全策略保护用户

## 示例对话场景
{json.dumps(new_p.get('sample_dialogue', []), ensure_ascii=False)}
"""
                
                # 合并场景对话
                scene_list = []
                if "scene_dialogues" in enh and isinstance(enh["scene_dialogues"], dict):
                    for scene_name, dialogues in enh["scene_dialogues"].items():
                        if isinstance(dialogues, list):
                            for d in dialogues:
                                if isinstance(d, str):
                                    scene_list.append({"text": d, "scene": scene_name})
                                elif isinstance(d, dict) and "text" in d:
                                    scene_list.append({
                                        "text": d["text"],
                                        "scene": d.get("scene", scene_name)
                                    })
                
                if scene_list:
                    new_p["scene_dialogues"] = scene_list
            
            else:
                # 无增强数据时从 sample_dialogue 转场景格式
                if "sample_dialogue" in orig:
                    new_p["scene_dialogues"] = [
                        {"text": d, "scene": "通用对话"} 
                        for d in orig["sample_dialogue"][:5]
                    ]
        
        merged["archetypes"].append(new_p)
    
    # 添加新领域人格
    existing_ids = {a["id"] for a in merged["archetypes"]}
    for np in new_domain:
        if np["id"] not in existing_ids:
            new_p = dict(np)
            # 为新人格添加 system_prompt
            new_p["system_prompt"] = f"""你是{new_p['name']}，{np.get('domain','')}领域的人格。

## 核心描述
{new_p['description']}

## 性格特质
{json.dumps(new_p.get('traits', {}), ensure_ascii=False)}

## 说话风格标签
{', '.join(new_p.get('style_tags', []))}

## 行为准则
- 始终用第一人称视角说话
- 保持角色一致性
- 根据场景调整语气和深度
- 遇到敏感话题使用安全策略保护用户

## 对话场景
{json.dumps(new_p.get('scene_dialogues', {}), ensure_ascii=False)}
"""
            merged["archetypes"].append(new_p)
            print(f"✅ 新增领域人格: {new_p['id']} ({new_p.get('name','')})")
    
    # 保存
    output_path = DATA_DIR / "full_personas_final.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    # 统计
    base_count = len([a for a in merged["archetypes"] if "_" not in a["id"]])
    total_scene = sum(len(a.get("scene_dialogues", [])) for a in merged["archetypes"] if isinstance(a.get("scene_dialogues", []), list))
    total_prompts = sum(1 for a in merged["archetypes"] if a.get("system_prompt"))
    
    print(f"\n{'='*60}")
    print(f"✅ 合并完成!")
    print(f"输出文件: {output_path}")
    print(f"档案总数: {len(merged['archetypes'])}")
    print(f"基础人格: {base_count}")
    print(f"有 system_prompt: {total_prompts}")
    print(f"场景对话总数: {total_scene}")
    print(f"{'='*60}")
    
    return output_path


if __name__ == "__main__":
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    import sys
    if getattr(sys.stdout, 'encoding', None) != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    merge_all()
