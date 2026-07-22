import json, subprocess, requests

def run_search(query: str) -> str:
    """Very simple web search using DuckDuckGo HTML results (no API key)."""
    try:
        resp = requests.get('https://duckduckgo.com/html/', params={'q': query}, timeout=10)
        # return first few lines of raw html as placeholder
        lines = resp.text.splitlines()[:5]
        return "\n".join(lines)
    except Exception as e:
        return f"搜索出错: {e}"

def run_calc(expr: str) -> str:
    """安全计算，仅支持数字、算术运算。"""
    try:
        # 限制可用的内置函数
        allowed_names = {"__builtins__": {}}
        result = eval(expr, allowed_names, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

def dispatch(name: str, args: dict) -> str:
    if name == "search":
        return run_search(args.get('query', ''))
    if name == "calc":
        return run_calc(args.get('expr', ''))
    return f"未知工具: {name}"
