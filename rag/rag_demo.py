"""
RAG (Retrieval-Augmented Generation) 综合技术演示
=================================================
本示例涵盖 RAG 系统中的 6 大核心技术模块：
  1. 多格式文档加载 (Loading)
  2. 智能文本切分 (Splitting)
  3. 向量化 + Chroma 向量数据库 (Embedding & Vector Store)
  4. 混合检索: BM25 关键词 + 向量语义 (Hybrid Search)
  5. 检索后上下文压缩 (Contextual Compression)
  6. 带来源引用的增强生成 (Generation with Source Attribution)
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# LangChain 核心组件导入
# ==========================================
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# 向量数据库 (Vector Database)
from langchain_chroma import Chroma

# 社区组件: 文档加载器 & 检索器 (langchain-community)
from langchain_community.document_loaders import TextLoader
from langchain_community.retrievers import BM25Retriever

# 文本切分
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Prompt 模板
from langchain.prompts import ChatPromptTemplate

# 输出解析
from langchain_core.output_parsers import StrOutputParser

# 检索器编排
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# LCEL 链路编排
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# ==========================================
# 1. 路径与环境配置 (Paths & Environment)
# ==========================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_PATH = PROJECT_ROOT / "env" / ".env"
CHROMA_DB_PATH = SCRIPT_DIR / "chroma_db"

# 模型配置
MODEL_CONFIG = {
    "base_url": "https://api.deepseek.com",
    "model_name": "deepseek-chat",
    "temperature": 0
}

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()


# ==========================================
# 2. 准备演示知识文档
# ==========================================
def create_knowledge_files():
    """创建多个知识文档，模拟真实的多源数据场景"""

    # 文档 1: LangChain 基础知识
    doc1_path = SCRIPT_DIR / "knowledge_langchain.txt"
    doc1_path.write_text("""\
LangChain 是目前最流行的大语言模型应用开发框架，由 Harrison Chase 于 2022 年创建。
它提供了模块化的组件体系，包括：模型 I/O (Model I/O)、检索 (Retrieval)、
代理 (Agents)、链 (Chains) 和记忆 (Memory) 等核心模块。

LangChain 的社区生态非常丰富，langchain-community 包集成了超过 700 个第三方组件，
涵盖了文档加载、向量数据库、嵌入模型、LLM 提供商等多种接口。
LCEL (LangChain Expression Language) 是其最新推荐的链路编排语法，
支持流式处理、异步调用和批量执行。
""", encoding="utf-8")

    # 文档 2: 向量数据库知识
    doc2_path = SCRIPT_DIR / "knowledge_vectordb.txt"
    doc2_path.write_text("""\
向量数据库是 RAG 系统的核心基础设施。它将文本转化为高维向量进行存储和检索。
常见的开源向量数据库包括：

Chroma：轻量级、易于集成的嵌入数据库，适合快速原型开发和中小规模应用。
支持持久化存储和元数据过滤。

FAISS：由 Meta(Facebook) 开源的高性能向量检索库，擅长大规模、高维度向量的近似最近邻搜索。
适合对检索速度有极高要求的生产环境。

Milvus：云原生的分布式向量数据库，支持万亿级向量数据，适合企业级大规模部署。

Weaviate：支持混合搜索（向量+关键词）的开源向量数据库，内置 GraphQL API。
""", encoding="utf-8")

    # 文档 3: RAG 进阶技术
    doc3_path = SCRIPT_DIR / "knowledge_rag_advanced.txt"
    doc3_path.write_text("""\
RAG（检索增强生成）的进阶技术包括：

混合检索 (Hybrid Search)：将 BM25 关键词检索与向量语义检索结合，
通过 EnsembleRetriever 加权融合两种检索结果，兼顾精确匹配与语义理解。

上下文压缩 (Contextual Compression)：使用 LLM 对检索到的文档进行二次精选，
仅保留与问题直接相关的内容片段，减少噪声干扰，提升生成质量。

重排序 (Reranking)：使用专门的 Cross-Encoder 模型对检索结果进行重新排序，
如 Cohere Rerank 或 bge-reranker，能显著提升检索准确率。

来源引用 (Source Attribution)：在生成回答时附带引用来源，
让用户能够追溯答案的知识依据，提升系统可信度。
""", encoding="utf-8")

    return [doc1_path, doc2_path, doc3_path]


# ==========================================
# 3. 初始化共享组件
# ==========================================
def init_llm():
    """初始化 DeepSeek LLM"""
    return ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=MODEL_CONFIG["base_url"],
        model=MODEL_CONFIG["model_name"],
        temperature=MODEL_CONFIG["temperature"]
    )


def init_embeddings():
    """初始化本地 HuggingFace Embedding 模型"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ==========================================
# 4. RAG 核心流程模块
# ==========================================

def step1_load_documents(file_paths):
    """
    [步骤 1] 多格式文档加载
    使用 langchain-community 提供的 TextLoader 加载多个文档。
    LangChain 还支持 PyPDFLoader、WebBaseLoader、CSVLoader 等 40+ 种格式。
    """
    print("\n" + "=" * 50)
    print("📄 步骤 1: 多格式文档加载 (Document Loading)")
    print("=" * 50)

    all_documents = []
    for path in file_paths:
        loader = TextLoader(str(path), encoding="utf-8")
        docs = loader.load()
        # 为每个文档添加元数据（来源标记）
        for doc in docs:
            doc.metadata["source"] = path.name
            doc.metadata["category"] = path.stem.replace("knowledge_", "")
        all_documents.extend(docs)
        print(f"  ✅ 已加载: {path.name} (元数据: category={docs[0].metadata['category']})")

    print(f"  📊 共加载 {len(all_documents)} 个文档")
    return all_documents


def step2_split_documents(documents):
    """
    [步骤 2] 智能文本切分
    RecursiveCharacterTextSplitter 会按 [\\n\\n, \\n, 。, ，, ' '] 的优先级
    递归切分文本，尽可能保持语义完整性。
    """
    print("\n" + "=" * 50)
    print("✂️ 步骤 2: 智能文本切分 (Text Splitting)")
    print("=" * 50)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,          # 每块最大 200 字符
        chunk_overlap=40,        # 相邻块重叠 40 字符，确保语义连续
        separators=["\n\n", "\n", "。", "，", " "],  # 中文友好的分隔符
    )
    splits = text_splitter.split_documents(documents)

    print(f"  ✅ 切分完成: {len(documents)} 个文档 → {len(splits)} 个语义块")
    for i, chunk in enumerate(splits[:3]):
        print(f"  📎 片段 {i+1} (来源: {chunk.metadata['source']}): "
              f"{chunk.page_content[:50]}...")

    return splits


def step3_build_vectorstore(splits, embeddings):
    """
    [步骤 3] 向量化 + Chroma 向量数据库
    将文本块转化为高维向量并存入 Chroma，支持持久化和元数据过滤。
    """
    print("\n" + "=" * 50)
    print("🗄️ 步骤 3: 向量数据库构建 (Vector Store - Chroma)")
    print("=" * 50)

    # 清理旧数据库，确保演示数据干净
    if CHROMA_DB_PATH.exists():
        shutil.rmtree(CHROMA_DB_PATH)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(CHROMA_DB_PATH),
        collection_metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
    )

    print(f"  ✅ Chroma 向量数据库构建成功")
    print(f"  📁 持久化路径: {CHROMA_DB_PATH}")
    print(f"  📊 索引文档数: {vectorstore._collection.count()}")

    # 演示元数据过滤 (Metadata Filtering)
    print("\n  --- 元数据过滤演示 ---")
    filtered_results = vectorstore.similarity_search(
        "向量数据库", k=2,
        filter={"category": "vectordb"}  # 仅在 vectordb 类别中检索
    )
    for i, doc in enumerate(filtered_results):
        print(f"  🔍 [过滤检索 {i+1}] (来源: {doc.metadata['source']}): "
              f"{doc.page_content[:60]}...")

    return vectorstore


def step4_hybrid_search(splits, vectorstore):
    """
    [步骤 4] 混合检索: BM25 + 向量检索
    通过 EnsembleRetriever 加权融合关键词检索和语义检索。
    """
    print("\n" + "=" * 50)
    print("🔀 步骤 4: 混合检索 (Hybrid Search = BM25 + Vector)")
    print("=" * 50)

    # BM25 关键词检索器
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 3

    # 向量语义检索器
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 混合检索器：BM25 权重 0.4，向量检索权重 0.6
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.4, 0.6]
    )

    # 对比演示
    test_query = "Chroma 和 FAISS 有什么区别？"
    print(f"  测试查询: '{test_query}'")

    bm25_docs = bm25_retriever.invoke(test_query)
    vector_docs = vector_retriever.invoke(test_query)
    hybrid_docs = ensemble_retriever.invoke(test_query)

    print(f"\n  📖 BM25 关键词检索结果 ({len(bm25_docs)} 条):")
    for doc in bm25_docs[:2]:
        print(f"     - [{doc.metadata['source']}] {doc.page_content[:60]}...")

    print(f"\n  🧠 向量语义检索结果 ({len(vector_docs)} 条):")
    for doc in vector_docs[:2]:
        print(f"     - [{doc.metadata['source']}] {doc.page_content[:60]}...")

    print(f"\n  🔀 混合检索结果 ({len(hybrid_docs)} 条):")
    for doc in hybrid_docs[:2]:
        print(f"     - [{doc.metadata['source']}] {doc.page_content[:60]}...")

    return ensemble_retriever


def step5_contextual_compression(ensemble_retriever, llm):
    """
    [步骤 5] 检索后上下文压缩
    使用 LLM 对检索结果进行二次精选，仅保留与问题直接相关的内容。
    """
    print("\n" + "=" * 50)
    print("🗜️ 步骤 5: 上下文压缩 (Contextual Compression)")
    print("=" * 50)

    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )

    test_query = "什么是混合检索？"
    print(f"  测试查询: '{test_query}'")

    # 压缩前
    raw_docs = ensemble_retriever.invoke(test_query)
    print(f"\n  📄 压缩前 ({len(raw_docs)} 条，原始内容):")
    for doc in raw_docs[:2]:
        print(f"     - {doc.page_content[:80]}...")

    # 压缩后
    compressed_docs = compression_retriever.invoke(test_query)
    print(f"\n  🗜️ 压缩后 ({len(compressed_docs)} 条，精选内容):")
    for doc in compressed_docs:
        print(f"     - {doc.page_content[:80]}...")

    return compression_retriever


def step6_generation_with_sources(retriever, llm):
    """
    [步骤 6] 带来源引用的增强生成
    在生成回答的同时，附带引用来源信息，提升可信度。
    """
    print("\n" + "=" * 50)
    print("🤖 步骤 6: 带来源引用的增强生成 (Generation + Source Attribution)")
    print("=" * 50)

    # 格式化检索到的文档（保留来源信息）
    def format_docs_with_sources(docs):
        formatted = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "未知来源")
            formatted.append(f"[来源 {i+1}: {source}]\n{doc.page_content}")
        return "\n\n".join(formatted)

    # 带来源引用的 Prompt 模板
    template = """你是一个专业的 AI 知识助手。请根据以下上下文回答问题。
要求：
1. 仅基于上下文内容作答，不要编造信息。
2. 在回答末尾标注你引用了哪些来源（如 [来源 1]、[来源 2]）。
3. 如果上下文不足以回答，请明确说明。

上下文:
{context}

问题: {question}

回答:"""
    prompt = ChatPromptTemplate.from_template(template)

    # 构建 RAG 链（使用 LCEL 管道语法）
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs_with_sources),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # 执行多个演示问题
    queries = [
        "LangChain 框架有哪些核心模块？",
        "在 RAG 系统中，混合检索相比纯向量检索有什么优势？",
    ]

    for query in queries:
        print(f"\n  ❓ [问题]: {query}")
        print("  🤖 [AI 思考中...]")
        response = rag_chain.invoke(query)
        print(f"  💬 [回答]:\n  {response}")
        print("  " + "-" * 40)


# ==========================================
# 5. 主程序入口
# ==========================================
def main():
    print("🌟" * 25)
    print("  RAG 综合技术演示 - 涵盖 6 大核心技术模块")
    print("  技术栈: LangChain + Chroma + HuggingFace + DeepSeek")
    print("🌟" * 25)

    # 初始化共享组件
    print("\n⏳ 正在初始化模型组件（首次运行可能需要下载 Embedding 模型）...")
    llm = init_llm()
    embeddings = init_embeddings()
    print("✅ 模型组件初始化完成\n")

    # 准备演示数据
    file_paths = create_knowledge_files()

    # 执行 RAG 全流程
    documents = step1_load_documents(file_paths)
    splits = step2_split_documents(documents)
    vectorstore = step3_build_vectorstore(splits, embeddings)
    ensemble_retriever = step4_hybrid_search(splits, vectorstore)
    compression_retriever = step5_contextual_compression(ensemble_retriever, llm)
    step6_generation_with_sources(compression_retriever, llm)

    print("\n" + "🎉" * 25)
    print("  RAG 演示全流程执行完毕！")
    print("🎉" * 25)


if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 错误: 请先在 env/.env 中配置 DEEPSEEK_API_KEY")
    else:
        main()
