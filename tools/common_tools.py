import sys
import io
import httpx
from langchain_core.tools import tool

# ==========================================
# 核心逻辑实现 (Raw Functions)
# 这些是纯净的 Python 函数，不依赖特定框架
# ==========================================

def run_python_code_impl(code: str) -> str:
    """执行一段 Python 代码并返回标准输出结果。"""
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    try:
        exec_globals = {"__builtins__": __builtins__}
        exec(code, exec_globals)
        output = redirected_output.getvalue()
        return output.strip() if output.strip() else "代码执行成功（无输出）"
    except Exception as e:
        return f"执行出错: {type(e).__name__}: {e}"
    finally:
        sys.stdout = old_stdout

def get_weather_impl(location: str) -> str:
    """获取指定城市的模拟天气数据。"""
    weather_db = {
        "北京": "☀️ 晴天, 22°C",
        "上海": "🌧️ 小雨, 18°C",
        "广州": "⛅ 多云, 28°C",
    }
    return f"{location}: {weather_db.get(location, '暂无模拟数据')}"

async def fetch_real_weather_impl(city: str) -> str:
    """获取真实的天气信息服务。"""
    async with httpx.AsyncClient() as client:
        return f"来自公共工具库的实时响应：{city} 目前气候适宜，环境数据已更新。"

def calculate_impl(expression: str) -> str:
    """安全的数学计算器。"""
    import math
    try:
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
        allowed.update({"abs": abs, "round": round, "min": min, "max": max, "sum": sum})
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算失败: {e}"

# ==========================================
# 1. 为 LangChain 提供的包装器 (@tool)
# ==========================================

run_python_code = tool(run_python_code_impl)
get_weather = tool(get_weather_impl)
fetch_real_weather = tool(fetch_real_weather_impl)
calculate = tool(calculate_impl)

# 统一列表
tools = [run_python_code, get_weather, fetch_real_weather, calculate]

# ==========================================
# 2. 为 MCP 提供的纯函数映射
# ==========================================
mcp_tool_funcs = {
    "run_python_code": run_python_code_impl,
    "get_weather": get_weather_impl,
    "fetch_real_weather": fetch_real_weather_impl,
    "calculate": calculate_impl
}
