import os
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv

# LangChain 核心组件导入
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# LangGraph 图形编排组件导入
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# 1. 环境准备：加载 .env 中的 API 密钥
load_dotenv()

# ==========================================
# 2. 定义 工具 (Tools) - 【LangChain 核心功能】
# ==========================================
@tool
def get_weather(location: str) -> str:
    """获取指定城市的天气状况。"""
    # 这里是一个纯模拟函数，实际可对接第三方 API (如和气象站集成)
    if "北京" in location:
        return "北京: 晴天, 气温 20°C"
    elif "上海" in location:
        return "上海: 阵雨, 气温 25°C"
    return f"{location}: 未知天气，可能还不错。"

@tool
def calculate(expression: str) -> str:
    """一个能够计算基础数学表达式的计算器。"""
    try:
        # 注意: 实际生产中应尽量避免 eval，此处仅作为演示用途
        return str(eval(expression))
    except Exception as e:
        return f"数学计算失败: {e}"

tools = [get_weather, calculate]

# ==========================================
# 3. 定义 状态 (State) - 【LangGraph 核心功能】
# ==========================================
# 图(Graph)中流转的核心数据结构，规定了每一次节点互相传递什么数据。
class AgentState(TypedDict):
    # 使用 `add_messages` 装饰器，让每次返回的 message 会 **追加** 给已有状态，而不是覆盖
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ==========================================
# 4. 初始化 模型与工具绑定 - 【LangChain 核心功能】
# ==========================================
# 借助完全兼容 OpenAI SDK 的特性，我们直接使用 ChatOpenAI 类接入 DeepSeek
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat", 
    temperature=0
)

# bind_tools 将 Python 函数转为符合 OpenAI API 标准的工具 schema，并植入给 LLM
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 5. 定义 节点逻辑 (Nodes) - 【LangGraph 核心功能】
# ==========================================
def agent_reasoning_node(state: AgentState):
    """
    负责进行"思考/推理"的节点。
    它接收当前历史消息，呼叫大模型。模型可能直接返回答案，也可能要求调用某个 Tool。
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    # 返回并追加新的消息回状态中
    return {"messages": [response]}

# LangGraph 预置的标准 Tool 节点：它探测消息里是否有 "tool_calls"，有的话会触发对应函数代码
tool_execution_node = ToolNode(tools)

# ==========================================
# 6. 构建并编译图状态 (Build Graph) - 【LangGraph 核心功能】
# ==========================================
# 初始化 StateGraph
workflow = StateGraph(AgentState)

# 注册我们的两个节点：名为 "agent" （推理）和 "tools" （执行工具）
workflow.add_node("agent", agent_reasoning_node)
workflow.add_node("tools", tool_execution_node)

# 设置逻辑边 (Edges) 和 路由 (Routing)
# (1) 程序的入口永远指向 agent 节点
workflow.add_edge(START, "agent")

# (2) agent 节点执行完之后我们要判断是否需要走到 action 或者 END
workflow.add_conditional_edges(
    "agent",           # 当前节点
    tools_condition,   # LangGraph 提供的一个标准预置路由逻辑（根据上一条回复里是否有 tool_call 作条件判断）
)

# (3) tools (即工具执行完毕) 之后，一定要返回给 agent，让 agent 继续基于得到的结果进行推理
workflow.add_edge("tools", "agent")

# (4) 编译 Workflow：我们接入 SqliteSaver 使图具备真实的磁盘级记忆能力
# 初始化 SQLite 数据库连接
# 注意：正式环境或者多线程环境建议 check_same_thread=False
conn = sqlite3.connect("memory.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
app = workflow.compile(checkpointer=memory)

# ==========================================
# 7. 主执行程序
# ==========================================
def print_welcome_message():
    """打印欢迎横幅信息"""
    print("=" * 50)
    print("🌟 欢迎体验 LangChain x LangGraph 智能引擎演示 🌟")
    print("目前具备技能：通过工具查询天气、使用计算器计算复杂数学表达式。")
    print("并拥有上下文记忆（Checkpoint）能力。")
    print("输入 'quit' 或 'exit' 以退出。")
    print("=" * 50)

def process_events(events):
    """解析并打印图在流转过程中产生的中间事件"""
    for event in events:
        # 拿到最新追加的一条消息
        latest_msg = event["messages"][-1]
        
        if isinstance(latest_msg, HumanMessage):
            # 用户刚发的消息，跳过显示
            continue
            
        elif isinstance(latest_msg, AIMessage):
            if latest_msg.tool_calls:
                # Model 要求调用工具
                for tc in latest_msg.tool_calls:
                    print(f"🤖 [Agent]: 决定调用工具 -> {tc['name']}，参数：{tc['args']}")
                    
        elif isinstance(latest_msg, ToolMessage):
             print(f"⚙️ [Tool执行]: '{latest_msg.name}' 响应结果 = {latest_msg.content}")

def get_final_response(app, config):
    """获取图完整执行完毕后的最终大模型回复"""
    final_state = app.get_state(config)
    final_message = final_state.values["messages"][-1]
    return final_message.content

def main():
    print_welcome_message()

    # config 将提供给 memory 区分这是针对哪个用户的记忆流水
    config = {"configurable": {"thread_id": "demo_user_001"}}

    while True:
        user_input = input("\n[您]: ")
        if user_input.lower() in ['quit', 'exit']:
            print("再见！感谢体验。")
            break
            
        print("\n--- 引擎后台思考过程流 ---")
        # 激活 workflow，通过 stream_mode="values" 我们可以在状态(State)每次发生更新时得到推送
        events = app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config,
            stream_mode="values" 
        )
        
        # 遍历与分发中间件流程打印
        process_events(events)
        
        print("-" * 26)
        
        # 打印经过图引擎全流程完毕后的最终回复
        final_answer = get_final_response(app, config)
        print(f"\n[AI助手]: {final_answer}")

if __name__ == "__main__":
    if "DEEPSEEK_API_KEY" not in os.environ or os.environ["DEEPSEEK_API_KEY"] == "":
        print("\n⚠️ 警告: 继续之前，请确认您已在 .env 文件中正确填写了 DEEPSEEK_API_KEY！\n")
    main()
