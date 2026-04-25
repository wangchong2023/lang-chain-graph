# LangGraph 模块化状态机引擎 (langgraph_engine)

本项目将智能体逻辑按照工程化标准进行了深度解耦，解决了包名冲突并提升了扩展性。

## 🏗️ 内核-插件架构

| 目录/文件 | 职责说明 | 关键点 |
| :--- | :--- | :--- |
| **`core/`** | 引擎内核 | 包含状态定义、节点逻辑、图构建器 |
| **`plugins/`** | 工具插件 | 存放自定义工具（如 `agent_tools.py`） |
| **`database/`** | 存储层 | 存放所有持久化 SQLite 数据库 |
| **`main.py`** | 应用入口 | 启动交互式对话 |
| **`langgraph.ipynb`**| 交互演示 | 专注智能体编排的 Notebook 示例 |

## 🛠️ 核心特性
- **MCP 实时集成**: 通过 `mcp_weather_bridge` 实现了与 MCP 服务端的跨模块联动，获取实时天气信息。
- **包名解耦**: 更名为 `langgraph_app` 以避免与第三方库冲突。
- **结构化引用**: 采用 Python 相对导入机制，支持作为包整体运行。
- **存储归一化**: 所有运行时生成的 `.sqlite` 文件均自动路由至 `database/` 目录。

## 🚀 快速开始

在项目根目录下执行：
```bash
python -m langgraph_engine.main
```

## 🧠 开发指南
- **添加新节点**: 在 `core/nodes.py` 中定义新函数，并在 `core/builder.py` 中注册。
- **添加新工具**: 在 `plugins/agent_tools.py` 中添加 `@tool` 函数。

---
*Powered by LangGraph_Engine @ 2026*
