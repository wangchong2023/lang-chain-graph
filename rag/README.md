# RAG (Retrieval-Augmented Generation) 综合技术演示

本项目是一个完整的 RAG 技术学习示例，使用 LangChain 编排框架，深度整合了 Chroma 向量数据库、HuggingFace 本地嵌入模型和 DeepSeek LLM，覆盖了 RAG 系统中**6 大核心技术模块**。

## 🚀 核心功能演示

| 模块 | 功能 | 代码对应 |
| :--- | :--- | :--- |
| 📄 多格式加载 | 从多个文本文件加载知识，自动标记元数据 | `step1_load_documents()` |
| ✂️ 智能切分 | 中文友好的递归切分，保证语义连续性 | `step2_split_documents()` |
| 🗄️ 向量数据库 | Chroma 持久化存储 + 元数据过滤检索 | `step3_build_vectorstore()` |
| 🔀 混合检索 | BM25 关键词 + 向量语义加权融合 | `step4_hybrid_search()` |
| 🗜️ 上下文压缩 | LLM 驱动的检索后精选，减少噪声 | `step5_contextual_compression()` |
| 🤖 来源引用生成 | 回答附带知识来源，提升可信度 | `step6_generation_with_sources()` |

## 🛠️ 关键开源技术栈

### 框架与编排
| 技术 | 说明 | 本项目中的作用 |
| :--- | :--- | :--- |
| **LangChain** | 顶级 LLM 应用开发框架 | 使用 LCEL 语法编排 RAG 链路，统一管理各组件 |
| **langchain-community** | 社区生态 (700+ 集成) | 提供 `TextLoader`、`BM25Retriever` 等核心组件 |

### 向量化与存储
| 技术 | 说明 | 本项目中的作用 |
| :--- | :--- | :--- |
| **Chroma** | 轻量级开源向量数据库 | 存储文档向量，支持持久化与元数据过滤检索 |
| **HuggingFace / Sentence-Transformers** | 开源 Embedding 模型 | `all-MiniLM-L6-v2` 模型，本地运行，无需额外 API |

### 检索增强技术
| 技术 | 说明 | 本项目中的作用 |
| :--- | :--- | :--- |
| **BM25** | 经典关键词检索算法 (TF-IDF 变体) | 精确匹配关键词，弥补向量检索对专有名词的不足 |
| **EnsembleRetriever** | LangChain 混合检索器 | 按权重 (0.4/0.6) 融合 BM25 与向量检索结果 |
| **ContextualCompressionRetriever** | 上下文压缩检索器 | 使用 LLM 对检索结果做二次精选，过滤噪声 |

### 大语言模型
| 技术 | 说明 | 本项目中的作用 |
| :--- | :--- | :--- |
| **DeepSeek** | 顶尖开源权重 LLM | 生成引擎 + 上下文压缩器，提供逻辑推理与中文处理能力 |

## 📂 目录结构
```
rag/
├── rag_demo.py                # 核心演示脚本 (6 大模块)
├── README.md                  # 技术方案文档 (本文件)
├── knowledge_langchain.txt    # 知识文档: LangChain 基础 (自动生成)
├── knowledge_vectordb.txt     # 知识文档: 向量数据库对比 (自动生成)
├── knowledge_rag_advanced.txt # 知识文档: RAG 进阶技术 (自动生成)
└── chroma_db/                 # Chroma 持久化存储目录 (自动生成)
```

## 🏁 快速开始

### 1. 环境变量
确保 `env/.env` 中配置了 DeepSeek API Key：
```env
DEEPSEEK_API_KEY=your_key_here
```

### 2. 安装依赖
```bash
pip install langchain langchain-openai langchain-huggingface langchain-chroma \
            langchain-community chromadb sentence-transformers rank_bm25 \
            python-dotenv pypdf beautifulsoup4
```

### 3. 运行演示
```bash
python rag/rag_demo.py
```

## 💡 RAG 技术流程图

```
用户提问
   │
   ├──→ BM25 关键词检索 ──┐
   │                       ├──→ EnsembleRetriever (加权融合)
   └──→ 向量语义检索 ──────┘
                                    │
                                    ▼
                          上下文压缩 (LLM 精选)
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Prompt + 检索上下文  │
                         │  + 来源引用标记       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                          DeepSeek LLM 生成回答
                          (附带 [来源] 引用标注)
```

## 🔬 各模块技术细节

### 1. 文档加载 (Loading)
使用 `langchain-community` 的 `TextLoader` 加载多个本地文档，并为每个文档自动添加 **元数据** (`source`, `category`)，为后续的元数据过滤检索提供基础。

LangChain 还支持的常见 Loader：`PyPDFLoader`（PDF）、`WebBaseLoader`（网页）、`CSVLoader`（表格）、`UnstructuredLoader`（通用格式）等。

### 2. 文本切分 (Splitting)
`RecursiveCharacterTextSplitter` 按优先级 `[\n\n, \n, 。, ，, 空格]` 递归切分文本，相比简单的按字符截断，能更好地保持语义完整性。

关键参数：
- `chunk_size=200`：每块最大 200 字符
- `chunk_overlap=40`：相邻块重叠 40 字符，防止信息在边界处丢失

### 3. 向量数据库 (Vector Store - Chroma)
- **向量化**：使用 `all-MiniLM-L6-v2` 模型将文本转为 384 维向量
- **索引**：Chroma 内部使用 HNSW 算法构建近似最近邻索引
- **持久化**：数据存储在本地 `chroma_db/` 目录
- **元数据过滤**：支持按 `category` 等字段做精确过滤，缩小检索范围

### 4. 混合检索 (Hybrid Search)
通过 `EnsembleRetriever` 将两种检索策略融合：
- **BM25 (权重 0.4)**：基于词频的经典检索，擅长精确匹配专有名词
- **向量检索 (权重 0.6)**：基于语义相似度，能理解同义词和语义关联

两者互补，比单一检索方式有显著的准确率提升。

### 5. 上下文压缩 (Contextual Compression)
使用 `LLMChainExtractor` 对检索到的文档做二次过滤：
- 输入：检索器返回的多个原始文档块
- 处理：LLM 判断每块内容与问题的相关性，提取核心片段
- 输出：仅保留与问题直接相关的精简内容

效果：减少 Prompt 中的噪声，提升最终生成质量。

### 6. 来源引用 (Source Attribution)
在 Prompt 中要求模型标注引用来源 `[来源 1]`、`[来源 2]`，使回答可追溯。这是企业级 RAG 系统的标准要求，能够：
- 提升用户信任度
- 支持答案验证
- 满足合规审计需求
