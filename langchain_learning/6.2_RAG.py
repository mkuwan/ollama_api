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
import pprint as pp
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter
import json
from langchain_community.retrievers import TavilySearchAPIRetriever
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
from langchain_core.documents import Document

# embeddings = OllamaEmbeddings(
#     model="kun432/cl-nagoya-ruri-large:latest",
#     base_url="http://localhost:11434",
# )

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434",
)


# GitLoader を使用してリポジトリからファイルを取得する場合はこちらを利用してください
# 取得後は実行する必要はないのでコメントアウトしてください
# def file_filter(file_path: str) -> bool:
#     return file_path.endswith(".md")

# documents = GitLoader(
#     clone_url="https://github.com/mkuwan/autogenProject",
#     repo_path="./langchain_learning/autogenProject",
#     branch="main",    
#     file_filter=file_filter,
# ).load()


# ./langchain_learning/autogenProject 配下のファイルで .md ファイルを取得　os.walk() で再帰的に取得
documents = []
text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=50)
for root, dirs, files in os.walk("./langchain_learning/autogenProject"):
    for file in files:
        if file.endswith(".md"):
            print(os.path.join(root, file))
            source_text = TextLoader(os.path.join(root, file), encoding='utf-8').load()
            documents.extend(text_splitter.split_documents(source_text))

try:
    db = Chroma.from_documents(documents, embeddings)
except Exception as e:
    print("エラーが発生しました")
    print(e)


prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。
    
    文脈:"""
    {context}
    """

    質問:"""
    {question}
    """
    ''')

model = ChatOpenAI(
    model="mistral:latest",
    temperature=0.3,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

retriever = db.as_retriever()

chain = (RunnableParallel(
    {
        "question": RunnablePassthrough(),  # 入力をそのまま出力する
        "context": retriever,
    }) | prompt | model | StrOutputParser())


for chunk in chain.stream("内容を要約してください"):
    print(chunk, end="", flush=True)

# result = chain.invoke("内容を要約してください")
# print(result)

