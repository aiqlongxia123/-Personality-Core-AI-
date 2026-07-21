# Personality Core — 人格AI系统

> 把"性格"变成可计算、可旋转、可克隆的东西。

基于向量嵌入空间的人格分析系统，对标全球美食厨房MCP架构：食材→风味空间，我们做人格→行为空间。

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行Demo
python scripts/demo.py

# 启动API服务
python api/server.py

# 启动Web UI
python ui/gradio_app.py
```

## 核心功能

- **嵌入** — 文本描述 → 人格向量
- **因子提取** — ICA分解出独立人格维度
- **聚类** — GMM划分人格原型
- **旋转(Morph)** — 沿方向轴微调人格
- **评分** — 两个人格的适配度
- **对比** — 多维度差异分析
- **情感引擎** — 情绪动态 + 关系阶段
- **记忆系统** — 三层记忆 + 成长日志

## 项目结构

```
personality-core/
├── src/personality_core/   # 核心算法
├── api/                    # FastAPI接口
├── ui/                     # Gradio Web UI
├── data/                   # 预置数据集
├── scripts/                # 训练/演示脚本
└── docs/                   # 文档
```

## License

MIT
