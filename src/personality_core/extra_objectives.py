import time
import random

def inference_latency(engine, descriptions, n_runs=3):
    """返回 **负的平均推理时间**（秒），因为 Optuna 只支持最大化。
    实现方式：随机抽取一条描述，用 engine.embed 进行向量化并计时。
    """
    if not hasattr(engine, "embed"):
        return 0.0
    total = 0.0
    for _ in range(n_runs):
        txt = random.choice(descriptions)
        start = time.perf_counter()
        _ = engine.embed(txt)  # 触发一次嵌入计算
        total += time.perf_counter() - start
    avg = total / n_runs
    # 为了最大化，返回负值（越小的时间 → 越大的返回值）
    return -avg

def gpu_memory_usage(engine, descriptions=None):
    """返回 **负的 GPU 已分配内存（MiB）**，若没有可用 GPU 或未安装 torch，返回 0。"""
    try:
        import torch
        if torch.cuda.is_available():
            # 触发一次张量分配以确保统计有数据
            _ = torch.randn(1, device="cuda")
            mem_bytes = torch.cuda.max_memory_allocated()
            mem_mib = mem_bytes / (1024 * 1024)
            return -mem_mib  # 最大化 → 负的内存使用（越小越好）
    except Exception:
        pass
    return 0.0
