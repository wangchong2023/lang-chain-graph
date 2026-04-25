# MCP (Model Context Protocol) 技术演示

MCP 是由 Anthropic 发布的开放标准，旨在解决 AI 模型与外部工具、数据源之间“接口不统一”的痛点。

## 🌟 核心价值
- **一次编写，到处运行**：你编写一个 MCP Server，它可以同时被 Cursor、Claude Desktop、IDE 插件等多个客户端直接调用，无需重复适配。
- **解耦架构**：模型作为“大脑”在云端或本地运行，MCP Server 作为“外挂”提供具体的能力（如读取数据库、查询实时天气）。

## 📂 目录说明
- `mcp_server_demo.py`: **服务端实现**。定义了工具（Tools）和资源（Resources）。
- `mcp_client_demo.py`: **客户端调用示例**。模拟了 AI 宿主环境如何通过协议连接并调用服务端能力。

## 🔌 跨模块集成
该模块已被本项目其他部分作为“能力提供者”调用：
- **`langgraph_app`**: 通过 `mcp_weather_bridge` 插件实时调用。
- **`rag_app`**: 在 **Active RAG** 模式下，作为实时数据源注入检索上下文。

## 🚀 运行与调用
1. **启动服务端**:
   ```bash
   python mcp/mcp_server_demo.py
   ```
2. **执行调用演示**:
   打开另一个终端，运行：
   ```bash
   python mcp/mcp_client_demo.py
   ```

## 🛠️ 进阶：在 IDE 中集成
你可以将 `mcp_server_demo.py` 的绝对路径配置到 Cursor 或 Claude Desktop 的 MCP 配置中，这样这些 AI 助手就能直接识别并使用你定义的 `fetch_real_weather` 工具。
