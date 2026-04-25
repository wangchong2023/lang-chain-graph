import os
import asyncio
from typing import Annotated, Sequence
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# ⚠️ 注意: 该文件为 LangChain/LangGraph 基础演示
# 已修复：使用 add_messages 确保消息流完整性
# ==========================================

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# 导入公共工具库
from tools.common_tools import tools

# ==========================================
# 1. 状态定义 (关键修复)
# ==========================================
class AgentState(Annotated[dict, "State"]):
    """
    使用 TypedDict 定义状态，并利用 add_messages 插件实现消息自动追加。
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ==========================================
# 2. 环境与路径配置
# ==========================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_PATH = PROJECT_ROOT / "env" / ".env"
DB_PATH = SCRIPT_DIR / "memory.sqlite"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# ==========================================
# 3. 初始化模型
# ==========================================
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    temperature=0
)
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 4. 节点逻辑
# ==========================================
async def agent_reasoning_node(state: dict):
    messages = state["messages"]
    # 打印调试信息
    # print(f"📡 [Legacy Agent] 历史消息数: {len(messages)}")
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

tool_execution_node = ToolNode(tools)

# ==========================================
# 5. 构建并编译图
# ==========================================
def create_app(memory):
    # ⚡ 关键：必须指定带有 add_messages 的状态结构
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_reasoning_node)
    workflow.add_node("tools", tool_execution_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    return workflow.compile(checkpointer=memory)

# ==========================================
# 6. 交互主循环
# ==========================================
async def main():
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 错误: 请配置 DEEPSEEK_API_KEY")
        return

    # 清理可能存在的脏数据库
    if DB_PATH.exists():
        try: os.remove(DB_PATH)
        except: pass

    async with AsyncSqliteSaver.from_conn_string(str(DB_PATH)) as memory:
        app = create_app(memory)
        config = {"configurable": {"thread_id": "legacy_verify_thread"}}

        print("=" * 50)
        print("🌟 LangChain Legacy 实时能力验证 🌟")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n[您]: ")
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                async for event in app.astream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config,
                    stream_mode="values"
                ):
                    if not event.get("messages"): continue
                    latest_msg = event["messages"][-1]
                    if isinstance(latest_msg, AIMessage) and latest_msg.tool_calls:
                        for tc in latest_msg.tool_calls:
                            print(f"🤖 [Agent]: 决定调用工具 -> {tc['name']}")
                    elif isinstance(latest_msg, ToolMessage):
                        print(f"⚙️ [Tool执行]: 结果已生成")

                final_state = await app.aget_state(config)
                print(f"\n[AI助手]: {final_state.values['messages'][-1].content}")
            except EOFError:
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已退出。")
