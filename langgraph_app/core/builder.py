from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import AgentState
from .nodes import agent_reasoning_node, tool_execution_node

def create_workflow():
    """
    构建 LangGraph 工作流拓扑（不含编译）。
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", agent_reasoning_node)
    workflow.add_node("tools", tool_execution_node)

    # 设置边
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow
