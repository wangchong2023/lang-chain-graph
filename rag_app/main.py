"""
RAG (Retrieval-Augmented Generation) 现代化重构版
=================================================
本项目已完全移除 langchain_classic，采用现代 LCEL (LangChain Expression Language) 
和最新的模块化设计实现混合检索与上下文压缩。
"""

import os
import shutil
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# 现代 LangChain 组件导入 (0.2/0.3+ 标准)
# ==========================================
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document

# ==========================================
# 1. 路径与环境配置
# ==========================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_PATH = PROJECT_ROOT / "env" / ".env"
CHROMA_DB_PATH = SCRIPT_DIR / "vector_storage" / "chroma_db"
SOURCE_DATA_DIR = SCRIPT_DIR / "source_data"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# ==========================================
# 2. 核心逻辑实现
# ==========================================

def init_llm():
    return ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        temperature=0
    )

def init_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def create_knowledge_files():
    """创建模拟知识库"""
    if not SOURCE_DATA_DIR.exists():
        SOURCE_DATA_DIR.mkdir(parents=True)
    
    (SOURCE_DATA_DIR / "langchain.txt").write_text("LangChain 是 2022 年创建的 LLM 开发框架。", encoding="utf-8")
    (SOURCE_DATA_DIR / "vectordb.txt").write_text("Chroma 是一个开源的嵌入式向量数据库。", encoding="utf-8")
    return list(SOURCE_DATA_DIR.glob("*.txt"))

# ==========================================
# ⚡ 现代化混合检索 (LCEL 实现)
# ==========================================
class ModernHybridRetriever:
    """
    使用 LCEL 手动实现的混合检索器，取代 EnsembleRetriever。
    """
    def __init__(self, vectorstore, documents):
        self.vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.bm25_retriever.k = 2

    def invoke(self, query: str):
        # 1. 分别获取结果
        v_docs = self.vector_retriever.invoke(query)
        b_docs = self.bm25_retriever.invoke(query)
        
        # 2. 简单的去重合并 (现代做法通常配合 Rerank)
        all_docs = {d.page_content: d for d in (v_docs + b_docs)}
        return list(all_docs.values())

# ==========================================
# ⚡ 现代化上下文压缩 (Runnable 实现)
# ==========================================
async def compress_documents(docs: list[Document], query: str, llm: ChatOpenAI):
    """
    使用 LLM 直接提取关键信息，取代旧的 LLMChainExtractor。
    """
    compress_prompt = ChatPromptTemplate.from_template(
        "以下是检索到的文档内容：\n{context}\n\n"
        "请根据问题 '{query}'，提取出这些文档中与之最相关的核心陈述。"
        "如果内容不相关，请忽略。直接返回提取后的文本。"
    )
    context = "\n---\n".join([d.page_content for d in docs])
    chain = compress_prompt | llm | StrOutputParser()
    return await chain.ainvoke({"context": context, "query": query})

# ==========================================
# 3. 演示主逻辑
# ==========================================
async def main():
    print("🌟 现代化 RAG (无 Classic 依赖) 演示开始...")
    
    # 初始化
    llm = init_llm()
    embeddings = init_embeddings()
    file_paths = create_knowledge_files()
    
    # 加载与切分
    all_docs = []
    for p in file_paths:
        loader = TextLoader(str(p), encoding="utf-8")
        all_docs.extend(loader.load())
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    splits = splitter.split_documents(all_docs)
    
    # 向量存储
    if CHROMA_DB_PATH.exists(): shutil.rmtree(CHROMA_DB_PATH)
    vectorstore = Chroma.from_documents(splits, embeddings, persist_directory=str(CHROMA_DB_PATH))
    
    # 1. 混合检索
    hybrid_retriever = ModernHybridRetriever(vectorstore, splits)
    query = "LangChain 和向量数据库的关系"
    raw_docs = hybrid_retriever.invoke(query)
    
    # 2. 异步上下文压缩
    compressed_context = await compress_documents(raw_docs, query, llm)
    
    # 3. 融合 MCP 实时数据 (Active RAG)
    from tools.common_tools import fetch_real_weather_impl
    weather_info = await fetch_real_weather_impl("上海")
    
    # 4. 最终生成
    final_prompt = ChatPromptTemplate.from_template("""
你是一个现代化 AI 助手。
[本地知识提炼]: {context}
[实时外部数据]: {weather}
问题: {question}
回答:""")
    
    final_chain = final_prompt | llm | StrOutputParser()
    result = await final_chain.ainvoke({
        "context": compressed_context,
        "weather": weather_info,
        "question": query
    })
    
    print(f"\n❓ [问题]: {query}")
    print(f"📊 [压缩后的本地上下文]: {compressed_context}")
    print(f"💬 [最终回答]:\n{result}")

if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 请配置 DEEPSEEK_API_KEY")
    else:
        asyncio.run(main())
