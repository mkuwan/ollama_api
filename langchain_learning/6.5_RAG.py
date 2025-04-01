from langchain_community.document_loaders import GitLoader
from langchain_community.document_loaders import TextLoader
import os
from langchain_text_splitters import CharacterTextSplitter
import pprint as pp
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from typing import Iterator
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import chain
import time
import re
import pprint as pp
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter
import json
from langchain_community.retrievers import TavilySearchAPIRetriever, BM25Retriever
import fitz
import pymupdf4llm
from tqdm import tqdm
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from enum import Enum
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel, Field
from langchain.load import dumps, loads


with open(".local_pass.json") as f:
    config = json.load(f)  # 1回だけ読み込む
    TAVILY_API_KEY = config["TAVILY_API_KEY"]
    LANGSMITH_API_KEY = config["LANGSMITH_API_KEY"]
    LANGSMITH_PROJECT = config["LANGSMITH_PROJECT"]
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT


embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434",
)

model = ChatOpenAI(
    # model="mistral:latest",
    # model="llama3.2",
    model="phi3",
    temperature=0.2,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)


# 6.3_RAG.pyで作成したVectorStoreを取得します。
def get_vector_store(collection_name) -> Chroma:
    """Chromaのインスタンスを取得します。

    Args:
        collection_name (str): コレクションの名前。

    Returns:
        Chroma: Chromaのインスタンス。
    """
    client = chromadb.PersistentClient(path="./langchain_learning/rag/chroma")

    if collection_name in client.list_collections():
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            client=client,
        )
    else:
        print(f"Collection '{collection_name}' does not exist. Please create it first.")
        return None
    



def use_plural_retriever(question: str, vector_store: Chroma):
    """複数のリソースを取得するためのリトリーバを設定します。

    Args:
        retriever (TavilySearchAPIRetriever): TavilySearchAPIRetrieverのインスタンス。
    """
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。
    
    文脈:"""
    {context}
    """

    質問:"""
    {question}
    """
    ''')

    langchain_document_retriever = retriever.with_config(
        {"run_name": "langchain_document_retriever"}
    )

    web_retriever = TavilySearchAPIRetriever(k=3).with_config(
        {"run_name": "web_retriever"}
    )

    class Route(str, Enum):
        langchain_document = "langchain_document"
        web = "web"

    class RouteOutput(BaseModel):
        route: Route

    route_prompt = ChatPromptTemplate.from_template("""\
    質問に回答するために適切なRetrieverを選択してください。

    質問: {question}
    """)

    route_chain = (
        route_prompt
        | model.with_structured_output(RouteOutput)
        | (lambda x: x.route)
    )


    def routed_retriever(input: dict[str, Any]) -> List[Document]:
        question = input["question"]
        route = input["route"]

        if route == Route.langchain_document:
            return langchain_document_retriever.invoke(question)
        elif route == Route.web:
            return web_retriever.invoke(question)
        else:
            raise ValueError(f"Invalid route: {route}")

    route_rag_chain = (
        {
            "question": RunnablePassthrough(),
            "route": route_chain,
        }
        | RunnablePassthrough.assign(context=routed_retriever)
        | prompt| model | StrOutputParser()
    )

    for chunk in route_rag_chain.stream(question):
        print(chunk, end="", flush=True)



def reciprocal_rank_fusion(results: list[list], k=10):
    fused_scores = {}
    for docs in results:
        # Assumes the docs are returned in sorted order of relevance
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # pp.pprint(f"reranked_results: {reranked_results}")
    return reranked_results


def use_hybrid_retriever_bm25_web_docs(question: str, vector_store: Chroma):
    """複数のリソースを取得するためのリトリーバを設定します。

    Args:
        retriever (TavilySearchAPIRetriever): TavilySearchAPIRetrieverのインスタンス。
    """
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。
    
    文脈:"""
    {context}
    """

    質問:"""
    {question}
    """
    ''')

    documents = []
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
    for root, dirs, files in os.walk("./langchain_learning/rag/java_docs/output_md"):
        for file in files:
            if file.endswith(".md"):
                print(os.path.join(root, file))
                source_text = TextLoader(os.path.join(root, file), encoding='utf-8').load()
                documents.extend(text_splitter.split_documents(source_text))


    langchain_document_retriever = retriever.with_config(
        {"run_name": "langchain_document_retriever"}
    )

    web_retriever = TavilySearchAPIRetriever(k=3).with_config(
        {"run_name": "web_retriever"}
    )

    bm25_retriever = BM25Retriever.from_documents(documents=documents).with_config(
        {"run_name": "bm25_retriever"}
    )

    hybrid_retriever = (
        RunnableParallel({
            "langchain_document_retriever": langchain_document_retriever,
            "web_retriever": web_retriever,
            "bm25_retriever": bm25_retriever,
        })
        | (lambda x: [x["langchain_document_retriever"], x["web_retriever"], x["bm25_retriever"]])
        | reciprocal_rank_fusion
    )


    hybrid_rag_chain = (
        {
            "question": RunnablePassthrough(),
            "context": hybrid_retriever,
        }
        | prompt| model | StrOutputParser()
    )

    for chunk in hybrid_rag_chain.stream(question):
        print(chunk, end="", flush=True)





if __name__ == '__main__':
    # VectorStoreの作成、元となるPDFファイルの読み込みなどは6.3_RAG.pyで行っているため、ここではスキップします。
    vector_store = get_vector_store("java_docs_index")

    question = "Javaのクラスの継承について教えてください。"
    use_plural_retriever(question, vector_store)


    question = "東京都の人口は？"
    use_plural_retriever(question, vector_store)


    question = "Javaのクラスついて教えてください。"
    use_hybrid_retriever_bm25_web_docs(question, vector_store)