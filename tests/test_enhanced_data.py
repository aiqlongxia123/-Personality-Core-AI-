"""
3. E2E 测试增加新数据验证
测试场景对话加载、126人档案完整性、system_prompt 功能
"""

import pytest
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


class TestEnhancedData:
    """增强后的数据文件测试"""
    
    @pytest.fixture(autouse=True)
    def load_data(self):
        import json
        with open(DATA_DIR / "full_personas.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def test_total_archetypes_count(self):
        """测试档案总数是否为 126+"""
        total = len(self.data["archetypes"])
        assert total >= 126, f"档案总数应为 >=126，当前为 {total}"
    
    def test_base_personas_have_system_prompt(self):
        """测试基础人格是否有 system_prompt"""
        base = [a for a in self.data["archetypes"] if "_" not in a["id"]]
        assert len(base) == 8, f"基础人格数量应为 8，当前 {len(base)}"
        
        for p in base:
            assert "system_prompt" in p, f"{p['id']} 缺少 system_prompt"
            assert len(p["system_prompt"]) > 50, f"{p['id']} system_prompt 过短"
    
    def test_scene_dialogues_loaded(self):
        """测试场景对话数据存在（支持 dict 和 list 两种格式）"""
        base = [a for a in self.data["archetypes"] if "_" not in a["id"]]
        for p in base:
            sd = p.get("scene_dialogues", [])
            assert sd is not None and len(sd) >= 3, f"{p['id']} 场景对话不足"
            # 如果是 list，检查每项有 text 字段
            if isinstance(sd, list):
                for item in sd[:3]:
                    assert isinstance(item, dict) and "text" in item, f"{p['id']} scene_dialogues 元素格式错误"
    
    def test_new_domain_personas_exist(self):
        """测试新增领域人格存在"""
        new_ids = {"curie_daughter", "freda_carlo", "jane_austen", "marie_curie", "woolf_daughter"}
        all_ids = {a["id"] for a in self.data["archetypes"]}
        
        for new_id in new_ids:
            assert new_id in all_ids, f"缺少新增人格: {new_id}"
    
    def test_domains_coverage(self):
        """测试领域覆盖至少 7 类"""
        domains = set(a.get("domain", "") for a in self.data["archetypes"] if a.get("domain"))
        expected = {"philosophy", "theology", "psychology", "literature", 
                    "improvised", "science", "art"}
        
        for domain in expected:
            assert domain in domains, f"缺少领域: {domain}"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
