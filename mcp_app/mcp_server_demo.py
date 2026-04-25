"""
MCP (Model Context Protocol) 服务端示例 (极简重构版)
==============================================
该示例演示了如何直接引用公共工具库的原始逻辑并发布为 MCP 服务。
不再包含任何本地定义的工具函数。
"""

from fastmcp import FastMCP
from tools.common_tools import fetch_real_weather_impl

# 1. 创建 MCP 实例
mcp = FastMCP("SharedToolService")

# 2. 直接注册公共库中的原始函数 (零包装)
mcp.tool(name="fetch_real_weather")(fetch_real_weather_impl)

# 3. 定义资源 (Resources)
@mcp.resource("config://app_settings")
def get_settings() -> str:
    """提供应用配置作为 MCP 资源。"""
    return "AppMode: Production\nLogLevel: Debug"

if __name__ == "__main__":
    mcp.run()
