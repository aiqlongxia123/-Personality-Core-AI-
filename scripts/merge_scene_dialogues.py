"""
修复：只合并基础人格的场景对话，不重复到变体
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def merge_base_only():
    """只合并基础人格（不带下划线的）"""
    
    # 读取原始数据
    with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
        original_data = json.load(f)
    
    # 读取场景对话数据
    with open(DATA_DIR / "scene_dialogues.json", "r", encoding="utf-8") as f:
        scene_data = json.load(f)
    
    scene_by_id = {p["id"]: p for p in scene_data["archetypes"]}
    
    merged_count = 0
    
    for i, orig in enumerate(original_data["archetypes"]):
        eid = orig["id"]
        
        # 跳过变体（带下划线的）
        if "_" in eid:
            continue
        
        # 查找对应的基础人格
        enh = scene_by_id.get(eid)
        if enh:
            # 更新描述
            if enh.get("description"):
                original_data["archetypes"][i]["description"] = enh["description"]
            
            # 添加场景对话
            scene_list = []
            for scene_name, dialogues in enh.get("scene_dialogues", {}).items():
                for d in dialogues:
                    if isinstance(d, dict):
                        scene_list.append({
                            "text": d.get("text", ""),
                            "scene": scene_name
                        })
                    else:
                        scene_list.append({
                            "text": str(d),
                            "scene": scene_name
                        })
            
            if scene_list:
                original_data["archetypes"][i]["scene_dialogues"] = scene_list
                merged_count += 1
    
    # 保存
    output_path = DATA_DIR / "full_personas_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)
    
    base_count = len([a for a in original_data["archetypes"] if "_" not in a["id"]])
    total_scenes = sum(len(a.get("scene_dialogues", [])) for a in original_data["archetypes"] if "_" not in a["id"])
    
    print(f"✅ 合并完成！输出: {output_path}")
    print(f"  基础人格数: {base_count}（其中 {merged_count} 个已增强）")
    print(f"  场景对话总数: {total_scenes}")


if __name__ == "__main__":
    merge_base_only()
