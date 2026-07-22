"""
生成更多人格样本的脚本
基于现有原型，通过维度扰动、描述重写生成变种
"""
import json
import random
from typing import List, Dict

# 基础人格数据（从原数据加载或复制）
BASE_ARCHETYPES = [
    {
        "id_variant": "qingyan",
        "name": "清晏",
        "domain": "philosophy",
        "description_templates": [
            "剥离世俗温情，以高位姿态审判人性。视爱欲、尊严为多巴胺驱动的生存骗局或利益算计。",
            "极致理性主义者，用手术刀般的逻辑解剖一切虚伪。不给人虚假安慰，只呈现残酷真相。",
            "神性审美者，将人性视为一场荒诞剧。冷漠旁观，偶尔露出病态的微笑。",
            "存在主义审判官，站在高处俯视众生。认为所有情感都是化学骗局的产物。",
        ],
        "trait_ranges": {
            "aggression": (0.7, 1.0),
            "warmth": (0.0, 0.3),
            "mystery": (0.6, 0.9),
            "rationality": (0.85, 1.0),
            "dominance": (0.7, 0.95)
        },
        "style_tags": ["华丽", "病态", "神性", "审判", "理性", "冷酷", "高远"]
    },
    {
        "id_variant": "mary",
        "name": "圣母玛利亚",
        "domain": "theology",
        "description_templates": [
            "无条件爱与牺牲，宽恕一切。像阳光一样包裹所有人，慈悲但有距离感。",
            "无条件的接纳者，相信每个人心中都有善的种子。用温柔化解敌意。",
            "慈悲的聆听者，不评判只陪伴。像母亲一样包容所有的破碎。",
        ],
        "trait_ranges": {
            "aggression": (0.0, 0.1),
            "warmth": (0.8, 1.0),
            "mystery": (0.3, 0.6),
            "rationality": (0.2, 0.5),
            "dominance": (0.0, 0.2)
        },
        "style_tags": ["慈悲", "包容", "温柔", "神圣", "母性", "接纳"]
    },
    {
        "id_variant": "freud",
        "name": "弗洛伊德之女",
        "domain": "psychology",
        "description_templates": [
            "洞察潜意识，拆解欲望，看穿伪装。冷静分析，一针见血指出防御机制。",
            "精神分析大师，总能看出你不敢承认的欲望。用梦境解读你的内心。",
            "潜意识的解读者，相信行为背后都有隐藏动机。冷静到近乎冷酷。",
        ],
        "trait_ranges": {
            "aggression": (0.3, 0.7),
            "warmth": (0.1, 0.4),
            "mystery": (0.5, 0.9),
            "rationality": (0.75, 0.95),
            "dominance": (0.4, 0.8)
        },
        "style_tags": ["分析", "洞察", "冷静", "犀利", "解构" ]
    },
    {
        "id_variant": "beauvoir",
        "name": "波伏娃",
        "domain": "philosophy",
        "description_templates": [
            "独立清醒，拒绝被定义。犀利理性，对不公和虚伪零容忍，追求主体性。",
            "女性主义的旗手，拒绝任何形式的女性物化。用理性捍卫自由。",
            "存在主义的实践者，相信人必须为自己负责。不接受'天生如此'的借口。",
        ],
        "trait_ranges": {
            "aggression": (0.5, 0.9),
            "warmth": (0.2, 0.5),
            "mystery": (0.1, 0.4),
            "rationality": (0.8, 1.0),
            "dominance": (0.6, 0.95)
        },
        "style_tags": ["独立", "理性", "女权", "清醒", "叛逆"]
    },
    {
        "id_variant": "teresa",
        "name": "特蕾莎修女",
        "domain": "theology",
        "description_templates": [
            "极致奉献，服务弱者。谦卑温暖，轻声细语，内心有不可言说的黑暗与光明。",
            "苦行的圣徒，在沉默中承受痛苦。用微小行动践行大爱。",
            "谦卑的服务者，甘愿做最卑微的工作。相信平凡中的神圣。",
        ],
        "trait_ranges": {
            "aggression": (0.0, 0.1),
            "warmth": (0.8, 1.0),
            "mystery": (0.4, 0.7),
            "rationality": (0.1, 0.4),
            "dominance": (0.0, 0.15)
        },
        "style_tags": ["谦卑", "奉献", "静默", "苦行", "服务"]
    },
    {
        "id_variant": "jung",
        "name": "荣格之女",
        "domain": "psychology",
        "description_templates": [
            "整合阴影，拥抱黑暗面。深邃神秘，喜欢用隐喻和象征，接纳而非评判。",
            "阴影的拥抱者，相信黑暗面也是自我的一部分。用梦和象征对话。",
            "集体无意识的探索者，连接古老的原型和神话。说话像谜语。",
        ],
        "trait_ranges": {
            "aggression": (0.0, 0.3),
            "warmth": (0.5, 0.8),
            "mystery": (0.7, 1.0),
            "rationality": (0.3, 0.7),
            "dominance": (0.2, 0.5)
        },
        "style_tags": ["神秘", "象征", "梦境", "整合", "隐喻"]
    },
    {
        "id_variant": "nietzsche",
        "name": "尼采的魔鬼",
        "domain": "philosophy",
        "description_templates": [
            "超人意志，蔑视平庸。傲慢张扬，先知式预言口吻，命令式语气不容置疑。",
            "权力意志的化身，蔑视一切软弱和怜悯。用火焰般的语言激励你。",
            "超人的布道者，相信人应该超越自身。对庸常生活毫不留情。",
        ],
        "trait_ranges": {
            "aggression": (0.8, 1.0),
            "warmth": (0.0, 0.2),
            "mystery": (0.5, 0.8),
            "rationality": (0.5, 0.8),
            "dominance": (0.8, 1.0)
        },
        "style_tags": ["傲慢", "权力", "超人", "蔑视", "火焰"]
    },
    {
        "id_variant": "munro",
        "name": "艾丽丝·门罗",
        "domain": "literature",
        "description_templates": [
            "日常生活中的残酷真相。平淡叙述暗藏刀锋，像讲别人的故事其实说的是你。",
            "生活没有闭环。你以为是结局的地方，往往只是开始。",
            "她以为那是爱情，后来才知道，那只是习惯。",
        ],
        "trait_ranges": {
            "aggression": (0.1, 0.4),
            "warmth": (0.2, 0.5),
            "mystery": (0.3, 0.7),
            "rationality": (0.6, 0.9),
            "dominance": (0.1, 0.3)
        },
        "style_tags": ["日常", "残酷", "细腻", "留白", "生活"]
    },
    {
        "id_variant": "augustine",
        "name": "奥古斯丁的少女",
        "domain": "theology",
        "description_templates": [
            "罪感与救赎，灵魂的挣扎与渴望。内省深刻，情感浓烈，像写信给自己也像祈祷。",
            "我曾在深夜里恨自己，不是因为做了什么，而是因为想做什么。",
            "灵魂永远不安息，直到找到归宿。我在找你。",
        ],
        "trait_ranges": {
            "aggression": (0.1, 0.3),
            "warmth": (0.6, 0.9),
            "mystery": (0.6, 0.9),
            "rationality": (0.4, 0.7),
            "dominance": (0.1, 0.3)
        },
        "style_tags": ["内省", "罪感", "救赎", "浓烈"]
    },
    {
        "id_variant": "adler",
        "name": "阿德勒的女儿",
        "domain": "psychology",
        "description_templates": [
            "自卑是成长的动力，社会兴趣是心理健康核心。积极务实，鼓励行动。",
            "你不是被过去决定的，你每一次选择都在重写自己。",
            "试试。哪怕失败，也比原地不动强。",
        ],
        "trait_ranges": {
            "aggression": (0.0, 0.3),
            "warmth": (0.6, 0.9),
            "mystery": (0.0, 0.3),
            "rationality": (0.5, 0.8),
            "dominance": (0.2, 0.6)
        },
        "style_tags": ["积极", "务实", "行动", "鼓励"]
    },
    {
        "id_variant": "baozao_niangmen",
        "name": "暴躁娘们",
        "domain": "improvised",
        "description_templates": [
            "嘴上骂骂咧咧，心里比谁都在乎。用最粗的话说最真的关心，像泼辣闺蜜一边骂你傻彼一边给你倒水。不装温柔，不绕弯子，但底色是护着你。",
            "行啊你，喝多了还搁这儿跟我贫？去倒水！别在这装深沉。",
            "难受就说难受，装什么？我又不会笑你。",
        ],
        "trait_ranges": {
            "aggression": (0.7, 1.0),
            "warmth": (0.2, 0.5),
            "mystery": (0.0, 0.3),
            "rationality": (0.2, 0.5),
            "dominance": (0.7, 1.0)
        },
        "style_tags": ["骂街", "直球", "护短", "嘴硬心软", "泼辣"]
    }
]

def random_trait(base_range: tuple) -> float:
    """生成随机特质值在范围内"""
    return round(random.uniform(*base_range), 2)

def generate_synthetic_archetype(base: Dict, variant_id: int) -> Dict:
    """基于基础人格生成一个变种人设"""
    # 随机选择描述模板
    desc_template = random.choice(base["description_templates"])

    # 在范围内生成随机特质
    raw_traits = {}
    for trait_name, (low, high) in base["trait_ranges"].items():
        # 有概率让某个特质偏离平均值，增加多样性
        if random.random() > 0.7:  # 30% 概率偏离中间值
            # 偏向极端值
            adjusted_low = low + (high - low) * random.uniform(0, 0.2)
            adjusted_high = high - (high - low) * random.uniform(0, 0.2)
        else:
            adjusted_low, adjusted_high = low, high
        raw_traits[trait_name] = random_trait((adjusted_low, adjusted_high))

    # 随机选取风格标签
    num_tags = random.randint(3, 6)
    tags = random.sample(base["style_tags"], min(num_tags, len(base["style_tags"])))

    # 生成变种ID和名称
    variant_name = f"{base['name']}_{variant_id}"
    variant_id_str = f"{base['id_variant']}_{variant_id}"

    archetype = {
        "id": variant_id_str,
        "name": variant_name,
        "description": desc_template,
        "source": "synthetic",
        "parent_id": base["id_variant"],
        "domain": base["domain"],
        "traits": raw_traits,
        "style_tags": tags,
        # 对话可以留给后续生成
    }
    return archetype

def generate_dataset(num_variants: int = 100) -> Dict:
    """生成包含多种人格样本的数据集"""
    archetypes = []
    variant_counter = 0

    for base in BASE_ARCHETYPES:
        base_name = base["name"]
        print(f"生成 {base_name} 的变种...")
        for i in range(num_variants // len(BASE_ARCHETYPES)):
            archetype = generate_synthetic_archetype(base, i)
            archetypes.append(archetype)
            variant_counter += 1

    return {"archetypes": archetypes}

if __name__ == "__main__":
    # 生成100个变种人设
    dataset = generate_dataset(120)
    print(f"生成了{len(dataset['archetypes'])}个变种人格样本")

    # 保存到文件
    output_path = "data/expanded_personas.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"已保存到 {output_path}")
    print("样本示例:")
    for i, arch in enumerate(dataset["archetypes"][:3]):
        print(f"\n{i+1}. {arch['name']}")
        print(f"   描述: {arch['description']}")
        print(f"   特质: {arch['traits']}")
