# AI-Learning: 2026 AI 全栈工程实践

本项目是一个基于 [AI 知识全栈工程路线](./doc/AI_Knowledge_Roadmap.md) 构建的学习与实验工程。

## 📁 目录结构 (已优化)

项目采用“内核-插件-数据”分离的工程化结构进行优化：

### 1. LangGraph 智能体应用 (`/langgraph_app`)
- **`core/`**: 存放 `builder.py`, `nodes.py`, `state.py` 等内核逻辑。
- **`tools/`**: 引用根目录的公共工具库，实现全站能力共享。
- **`database/`**: 统一存放所有 SQLite 检查点文件。
- **`main.py`**: 模块化后的交互主入口。
- **`langgraph.ipynb`**: 专注智能体编排的笔记演示。

### 2. LangChain 基础应用 (`/langchain_app`)
- `main.py`: 包含基础的单文件智能体演示。
- `langchain.ipynb`: 包含 LCEL、Prompt 等基础教学示例。

### 3. RAG 检索增强生成应用 (`/rag_app`)
- `main.py`: RAG 全链路演示入口。
- `source_data/`: 原始知识文档存储。
- `vector_storage/`: ChromaDB 向量索引存储。
- `README.md`: 详细的 RAG 技术方案说明。

### 4. 前沿技术演示 (`/mcp_app`)
- `mcp_server_demo.py`: 演示了如何按照 MCP 标准定义远程服务。
- `mcp_client_demo.py`: MCP 客户端模拟调用脚本。
- **`tools/mcp_server.py`**: **【核心】** 全站统一公共工具服务。

### 5. 基础设施
- `doc/`: 全栈 AI 知识手册。
- `env/`: 环境配置与虚拟环境。
- `requirements.txt`: 项目依赖清单。

## 🚀 运行指南

1. **配置环境**: 编辑 `env/.env` 填写 API Key。
2. **运行智能体**: `python -m langgraph_app.main`
3. **运行 RAG 演示**: `python rag_app/main.py`

---
*Optimized and Modularized by Antigravity AI @ 2026*
