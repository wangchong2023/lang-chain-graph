import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 立即加载环境变量
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_PATH = PROJECT_ROOT / "env" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# 导入内部模块
from .core.builder import create_workflow

# ==========================================
# 1. 路径配置
# ==========================================
DB_PATH = SCRIPT_DIR / "database" / "modular_memory.sqlite"

# ==========================================
# 2. 交互逻辑
# ==========================================
async def process_events(events_stream):
    async for event in events_stream:
        if "messages" not in event:
            continue
            
        latest_msg = event["messages"][-1]
        if isinstance(latest_msg, AIMessage) and latest_msg.tool_calls:
            for tc in latest_msg.tool_calls:
                print(f"🤖 [Agent]: 决定调用工具 -> {tc['name']}")
        elif isinstance(latest_msg, ToolMessage):
             print(f"⚙️ [Tool执行]: 响应结果 = {latest_msg.content}")

async def main():
    if "DEEPSEEK_API_KEY" not in os.environ:
        print("⚠️ 请在 .env 中设置 DEEPSEEK_API_KEY")
        return

    # ⚡ 使用异步上下文管理器初始化持久化层
    async with AsyncSqliteSaver.from_conn_string(str(DB_PATH)) as memory:
        # 创建并编译应用
        workflow = create_workflow()
        app = workflow.compile(checkpointer=memory)
        
        # 使用新鲜的 thread_id 避免读取到脏状态
        config = {"configurable": {"thread_id": "modular_user_fresh_001"}}

        print("=" * 50)
        print("🌟 LangGraph 模块化架构演示 (异步/持久化模式) 🌟")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n[您]: ")
                if user_input.lower() in ['quit', 'exit']:
                    break
                    
                print("\n--- 思考过程 ---")
                events_stream = app.astream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config,
                    stream_mode="values" 
                )
                await process_events(events_stream)
                
                final_state = await app.aget_state(config)
                print(f"\n[AI助手]: {final_state.values['messages'][-1].content}")
            except EOFError:
                break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已退出。")
