from langchain_community.document_loaders import GitLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
import os
import asyncio
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
import nest_asyncio
from ragas.testset import TestsetGenerator
from ragas.llms import LangchainLLMWrapper
from ragas.llms import LlamaIndexLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate
from langchain_openai import OpenAIEmbeddings
from langsmith import Client as LangsmithClient
from ragas.testset.synthesizers.multi_hop import (
    MultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer,
)
from ragas.testset.synthesizers.single_hop.specific import (
    SingleHopSpecificQuerySynthesizer,
)




with open(".local_pass.json") as f:
    config = json.load(f)  # 1回だけ読み込む
    TAVILY_API_KEY = config["TAVILY_API_KEY"]
    LANGSMITH_API_KEY = config["LANGSMITH_API_KEY"]
    LANGSMITH_PROJECT = config["LANGSMITH_PROJECT"]
    # os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    # os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    # os.environ["LANGSMITH_TRACING"] = "true"
    # os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    # os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT


# embeddings = OllamaEmbeddings(
#     model="mxbai-embed-large",
#     base_url="http://localhost:11434",
# )

ollama_embeddings = OpenAIEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434",
    api_key="ollama",
)

ollama_model = ChatOpenAI(
    # model="mistral:latest",
    model="llama3.2",
    # model="phi3",
    temperature=0.2,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

nest_asyncio.apply()

# ChatModel定義
generator_model = LangchainLLMWrapper(langchain_llm=ollama_model)

# EmbeddingsModel定義
generator_embeddings = LangchainEmbeddingsWrapper(embeddings=ollama_embeddings)

# Generatorの生成
generator = TestsetGenerator(llm=generator_model, embedding_model=generator_embeddings)


# 6.3_RAG.pyで作成したVectorStoreを取得します
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
            embedding_function=ollama_embeddings,
            client=client,
        )
    else:
        print(f"Collection '{collection_name}' does not exist. Please create it first.")
        return None
    

def load_md_documents(path: str) -> List[Document]:
    # documents = []
    # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    # for root, dirs, files in os.walk(path):
    #     for file in files:
    #         if file.endswith(".md"):
    #             print(os.path.join(root, file))
    #             source_text = TextLoader(os.path.join(root, file), encoding='utf-8').load()
    #             documents.extend(text_splitter.split_documents(source_text))

    # return documents

    # テストセット生成のベースとなる文章をロード
    loader = DirectoryLoader(
        path,
        glob="**/*.txt",
        loader_cls=lambda p: TextLoader(p, encoding="utf-8")  # エンコーディングを指定
    )
    documents = loader.load()
    return documents



# Ragasが使用するメタデータである「filename」を設定します。
def set_mata_data(documents: List[Document]) -> List[Document]:
    for doc in documents:
        # doc.metadata["filename"]を設定します。
        doc.metadata["filename"] = doc.metadata["source"]
        # pp.pprint(doc.metadata)
    return documents





async def main():
    documents = load_md_documents("./langchain_learning/rag/ragas/")

    print(f"Number of documents: {len(documents)}")

    # documents = set_mata_data(documents)

    # #Synthesizerのインスタンスを生成
    # synthesizer = SingleHopSpecificQuerySynthesizer(llm=generator_model)
    # #シンセサイザーのプロンプトに日本語を適用
    # adapted_prompts = await synthesizer.adapt_prompts("japanese", generator_model)
    # #プロンプトをセット
    # synthesizer.set_prompts(**adapted_prompts)

    # #generate_with_langchain_docsに引き渡すためのデータ整備
    # query_distribution = [
    #     (synthesizer, 1.0) #1.0は割合を表し、今回はこのSynthesizerを100%利用することを表す。他のSynthesizerと組み合わせる事も可能。
    # ]


    # テストセットを生成します。
    testset = generator.generate_with_langchain_docs(
        documents=documents, 
        testset_size=3,
        # query_distribution=query_distribution
        )

    df = testset.to_pandas()

    # データフレームをCSVファイルとして保存
    csv_file_path = "./generated_testset.csv"
    df.to_csv(csv_file_path, index=False)



if __name__ == '__main__':
    asyncio.run(main())
