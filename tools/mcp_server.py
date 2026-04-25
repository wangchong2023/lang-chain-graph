"""
全站公共工具 MCP 服务端 (Unified Tool Server)
===========================================
该服务通过遍历 tools/common_tools.py 中的原始函数映射，
一键发布所有能力为标准 MCP 接口。
"""

from fastmcp import FastMCP
from tools.common_tools import mcp_tool_funcs

# 1. 创建统一服务实例
mcp = FastMCP("GlobalAgentTools")

# 2. 动态注册所有工具
for name, func in mcp_tool_funcs.items():
    # 动态挂载原始函数
    mcp.tool(name=name)(func)

if __name__ == "__main__":
    print("🚀 全站公共工具 MCP 服务正在启动...")
    print(f"📦 已挂载工具: {list(mcp_tool_funcs.keys())}")
    mcp.run()
