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

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434",
)

model = ChatOpenAI(
    model="mistral:latest",
    temperature=0.3,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

# HyDE（Hypothetical Document Embeddings） 
# シンプルなRAGの構成では、ユーザーの質問に対して埋め込みベクトルの類似度の高いドキュメントを検索します。
# しかし、実際に検索したいのは、質問に類似するドキュメントではなく、回答に類似するドキュメントです。
# そこで、HyDE（Hypothetical Document Embeddings）注3という手法があります。
# HyDEでは、ユーザーの質問に対してLLMに仮説的な回答を推論させ、その出力を埋め込みベクトルの類似度検索に使用します。


hypothetical_prompt = ChatPromptTemplate.from_template(
"""
次の質問に回答する一文を書いてください

質問:
{question}
""")




