from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    图中流转的核心状态数据结构。
    messages: 存储对话历史，使用 add_messages 确保消息是追加而非覆盖。
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
