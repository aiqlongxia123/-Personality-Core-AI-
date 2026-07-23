"""
完善版人格增强 - 合并 enhanced_base + scene_dialogues + 新增领域
生成 full_personas_v2.json
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def merge_all():
    """合并所有增强数据"""
    
    # 读取原始数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        original = json.load(f)
    
    # 读取增强基础数据（含场景对话）
    with open(DATA_DIR / "enhanced_base_personas.json", "r", encoding="utf-8") as f:
        enhanced = json.load(f)
    
    # 读取拓展新人物
    with open(DATA_DIR / "scene_dialogues_extended.json", "r", encoding="utf-8") as f:
        extended = json.load(f)
    
    enhanced_map = {p["id"]: p for p in enhanced["archetypes"]}
    extended_map = {p["id"]: p for p in extended["archetypes"] if p["id"] not in enhanced_map}
    
    merged = {"archetypes": []}
    
    for orig in original["archetypes"]:
        eid = orig["id"]
        new_p = dict(orig)
        
        # 跳过变体，只处理基础人格
        if "_" not in eid:
            enh = enhanced_map.get(eid)
            if enh:
                new_p["description"] = enh.get("description", orig.get("description", ""))
                new_p["scene_dialogues"] = []
                
                if "scene_dialogues" in enh:
                    for scene_name, dialogues in enh["scene_dialogues"].items():
                        for d in dialogues:
                            text = d if isinstance(d, str) else d.get("text", "")
                            new_p["scene_dialogues"].append({
                                "text": text,
                                "scene": scene_name
                            })
                elif "sample_dialogue" in enh:
                    # fallback: 使用旧格式
                    for i, d in enumerate(enh["sample_dialogue"]):
                        new_p["scene_dialogues"].append({
                            "text": d,
                            "scene": f"场景{i+1}"
                        })
                
                print(f"✅ {eid}: {len(new_p['scene_dialogues'])} 条场景对话")
        
        merged["archetypes"].append(new_p)
    
    # 添加拓展的新人格
    for eid, p in extended_map.items():
        merged["archetypes"].append(p)
        print(f"🆕 {p['name']} ({p['domain']})")
    
    # 保存
    output_path = DATA_DIR / "full_personas_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    base_count = len([a for a in merged["archetypes"] if "_" not in a["id"]])
    total_scenes = sum(len(a.get("scene_dialogues", [])) for a in merged["archetypes"] if "_" not in a["id"])
    total_dialogues = sum(len(a.get("scene_dialogues", [])) for a in merged["archetypes"])
    
    print(f"\n{'='*50}")
    print(f"合并完成！输出: {output_path}")
    print(f"总档案数: {len(merged['archetypes'])}")
    print(f"基础人格: {base_count}")
    print(f"基础场景对话: {total_scenes}")
    print(f"全部对话: {total_dialogues}")


if __name__ == "__main__":
    import os
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    import sys
    if getattr(sys.stdout, 'encoding', None) != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    merge_all()
