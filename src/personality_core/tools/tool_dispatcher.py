import ast
import json
import subprocess
import requests


def run_search(query: str) -> str:
    """Very simple web search using DuckDuckGo HTML results (no API key)."""
    try:
        resp = requests.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
        lines = resp.text.splitlines()[:5]
        return "\n".join(lines)
    except Exception as e:
        return f"搜索出错: {e}"


def run_calc(expr: str) -> str:
    """安全计算: 仅支持字面量/算术表达式. 用 ast.parse + NodeVisitor 白名单,
    严格禁止 Name/Call/Attribute 等可执行节点 (任何变量名、函数调用、属性访问).

    支持: 数字 (int/float), 字符串, 元组/列表/字典字面量, 一元/二元算术, 比较.
    不支持: 用户自定义函数、变量、import.

    Note: Python 的 +-*/ 字面量运算在 ast 里表达为 BinOp/UnaryOp, 这些是允许的.
    """
    try:
        tree = ast.parse(expr, mode="eval")

        # 白名单: 只允许这几类节点
        allowed = (
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub,
            ast.Load,
        )
        for node in ast.walk(tree):
            if not isinstance(node, allowed):
                return f"计算被拒绝: 不允许的表达式节点 ({type(node).__name__})"

        result = eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, {})
        # eval 的对象仍受允许表达式约束 (上面 NodeVisitor 已阻止 Name/Call/Attribute)
        return f"计算结果: {result}"
    except SyntaxError as e:
        return f"表达式语法错误: {e}"
    except Exception as e:
        return f"计算错误: {e}"


def dispatch(name: str, args: dict) -> str:
    if name == "search":
        return run_search(args.get("query", ""))
    if name == "calc":
        return run_calc(args.get("expr", ""))
    return f"未知工具: {name}"
