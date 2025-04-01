# Q&A Application
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
from langchain_core.pydantic_v1 import BaseModel, Field
import time
import re
import pprint as pp
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.runnables.utils import ConfigurableField
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
    Annotated
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
import operator
from langgraph.graph import StateGraph
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver




with open(".local_pass.json") as f:
    config = json.load(f)  # 1回だけ読み込む
    TAVILY_API_KEY = config["TAVILY_API_KEY"]
    LANGSMITH_API_KEY = config["LANGSMITH_API_KEY"]
    QA_PROJECT = config["QA_PROJECT"]
    # os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
    # os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    # os.environ["LANGCHAIN_TRACING"] = "true"
    # os.environ["LLANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    # os.environ["LANGCHAIN_PROJECT"] = QA_PROJECT



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
    # model="llama3.2",        
    model="phi4",    
    # model="phi3",              
    temperature=0.1,
    base_url="http://localhost:11434/v1/",
    api_key="ollama", 
)

# グラフのステートを定義
class State(BaseModel):
    query: str
    messages: Annotated[list[BaseMessage], operator.add] = Field(default=[])

# メッセージを追加するノード関数
def add_message(state: State) -> dict[str, Any]:
    additional_messages = []
    if not state.messages:
        additional_messages.append(
            SystemMessage(content="あなたは最小限の応答をする対話エージェントです。")
        )
    additional_messages.append(HumanMessage(content="\n\n" + state.query + "\n\n"))
    return {"messages": additional_messages}

# LLMからの応答を追加するノード関数
def llm_response(state: State) -> dict[str, Any]:
    llm = ollama_model
    ai_message = llm.invoke(state.messages)
    # ai_message.content に改行を追加
    ai_message.content = ai_message.content + "\n\n"
    return {"messages": [ai_message]}


def print_checkpoint_dump(checkpointer: BaseCheckpointSaver, config: RunnableConfig):
    checkpoint_tuple = checkpointer.get_tuple(config)

    print("チェックポイントデータ:")
    pp.pprint(checkpoint_tuple.checkpoint)
    print("\nメタデータ:")
    pp.pprint(checkpoint_tuple.metadata)


if __name__ == "__main__":

    # グラフを設定
    graph = StateGraph(State)
    graph.add_node("add_message", add_message)
    graph.add_node("llm_response", llm_response)

    graph.set_entry_point("add_message")
    graph.add_edge("add_message", "llm_response")
    graph.add_edge("llm_response", END)

    # チェックポインターを設定
    checkpointer = MemorySaver()
    
    # グラフのコンパイル
    compiled_graph = graph.compile(checkpointer=checkpointer)
    
    # グラフの実行
    config = {"configurable": {"thread_id": "example-1"}}
    user_query = State(query="私の好きなものはずんだ餅です。覚えておいてね。")

    for chunk, meta in compiled_graph.stream(user_query, config=config, stream_mode="messages"):
        print(chunk.content, end="", flush=True)

    # for checkpoint in checkpointer.list(config):
    #     print(checkpoint)

    # print_checkpoint_dump(checkpointer, config)

    user_query = State(query="私の好物は何か覚えてる？")
    for chunk, meta in compiled_graph.stream(user_query, config=config, stream_mode="messages"):
        print(chunk.content, end="", flush=True)


    # for checkpoint in checkpointer.list(config):
    #     print(checkpoint)

    # print_checkpoint_dump(checkpointer, config)
    
    print(f"{'*' * 20} 新しいセッションを開始 {'*' * 20}")
    config = {"configurable": {"thread_id": "example-2"}}
    user_query = State(query="私の好物は何？")
    for chunk, meta in compiled_graph.stream(user_query, config=config, stream_mode="messages"):
        print(chunk.content, end="", flush=True)