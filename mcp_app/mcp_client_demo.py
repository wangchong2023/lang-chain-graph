"""
MCP (Model Context Protocol) 客户端调用模拟
==========================================
该脚本模拟了一个 AI 宿主（如 Cursor 或自定义 Agent）如何通过协议
调用我们在 mcp_server_demo.py 中定义的工具。
"""

import asyncio
import json

# 模拟 MCP 客户端行为
async def mock_mcp_call():
    print("=" * 50)
    print("🌐 MCP 客户端连接中...")
    print("=" * 50)
    
    # 1. 模拟服务发现 (Discovery)
    # 实际上 MCP 客户端会读取服务器暴露的 JSON-RPC 描述
    available_tools = [
        {
            "name": "fetch_real_weather",
            "description": "获取真实天气信息的 MCP 工具",
            "input_schema": {"city": "string"}
        }
    ]
    
    print(f"✅ 发现可用 MCP 工具: {[t['name'] for t in available_tools]}")

    # 2. 模拟工具调用 (Call Tool)
    # 假设 AI 模型识别出意图，决定调用天气工具
    target_city = "北京"
    print(f"\n🤖 [AI 决策]: 准备调用远程 MCP 工具 -> fetch_real_weather, 参数: {target_city}")
    
    # 这里我们通过打印来展示协议交互的过程
    protocol_msg = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "fetch_real_weather",
            "arguments": {"city": target_city}
        },
        "id": 1
    }
    
    print(f"📤 [协议请求]: {json.dumps(protocol_msg, ensure_ascii=False)}")
    print("... 等待服务端响应 ...")
    
    # 模拟接收到服务端的回复 (由于服务端在不同进程，此处仅展示逻辑)
    mock_response = {
        "jsonrpc": "2.0",
        "result": {
            "content": [
                {"type": "text", "text": f"MCP 服务器响应：{target_city} 目前天气晴朗，由 MCP 协议转发。"}
            ]
        },
        "id": 1
    }
    
    print(f"📥 [协议响应]: {json.dumps(mock_response, ensure_ascii=False)}")
    print(f"\n✨ [最终结果]: {mock_response['result']['content'][0]['text']}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(mock_mcp_call())
