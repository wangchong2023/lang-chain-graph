import os
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from .state import AgentState
from tools.common_tools import tools

# 初始化模型
# 注意：在异步环境下，我们依然可以统一配置模型
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    temperature=0
)

# 绑定工具
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 节点逻辑
# ==========================================

async def agent_reasoning_node(state: AgentState):
    """
    异步推理节点：负责调用大模型并决定下一步行动。
    """
    messages = state["messages"]
    
    # 打印当前消息序列，用于调试工具调用链
    msg_types = [type(m).__name__ for m in messages]
    print(f"📡 [Node:Agent] 发送至 LLM 的消息序列: {msg_types}")
    
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

# 工具执行节点 (ToolNode 自动支持异步工具)
tool_execution_node = ToolNode(tools)
