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

ollama_model_one_number = ChatOpenAI(
    # model="mistral:latest",   #だめでした
    # model="llama3.2",        
    model="phi4",    
    # model="phi3",              #だめでした     
    temperature=0.1,
    base_url="http://localhost:11434/v1/",
    api_key="ollama", 
    max_tokens=1,
).configurable_fields(
    max_tokens=ConfigurableField(
        id="output_token_number", 
        name="Max tokens in the output",
        description="The maximum number of tokens in the output")
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

# Role
ROLES = {
    "1": {
        "name": "一般知識エキスパート",
        "description": "幅広い分野の一般的な質問に答える",
        "details": "幅広い分野の一般的な質問に対して、正確でわかりやすい回答を提供してください。"
    },
    "2": {
        "name": "生成AIエキスパート",
        "description": "生成AIの技術に関する専門的な質問に答える",
        "details": "生成AIや関連製品、技術に関する専門的な質問に対して、最新の情報と深い洞察を提供してください。"
    },
    "3": {
        "name": "カウンセラー",
        "description": "個人的な悩みや心理的な問題に対してサポートを提供する",
        "details": "個人的な悩みや心理的な問題に対して、共感的で支援的な回答を提供し、可能であれば適切なアドバイスも行ってください。"
    }
}


# ステートの定義
class State(BaseModel):
    query: str = Field(
        ...,
        description="ユーザーからの質問",
    )

    current_role: str = Field(
        default="",
        description="選択された回答ロール",
    )

    messages: Annotated[list[str], operator.add] = Field(
        default=[],
        description="回答履歴",
    )

    current_judge: bool = Field(
        default=False,
        description="品質チェックの結果",
    )

    judgement_reason: str = Field(
        default="",
        description="品質チェックの判定理由",
    )



# selectionノードの実装
# 回答ロールを選択するノード
def selection_node(state: State) -> dict[str, Any]:
    query = state.query
    role_options = "\n".join([f"{k}. {v['name']}: {v['description']}" for k, v in ROLES.items()])
    
    prompt = ChatPromptTemplate.from_template(
    """質問を分析し、最も適切な回答担当ロールを選択し、番号のみで回答してください。説明文は不要です。

    選択肢:
    {role_options}
    

    質問: {query}

    回答例: 1
    回答例: 2
    回答例: 3
    """.strip())

    # 選択肢の番号のみを返すことを期待したいため、max_tokensの値を1に変更
    chain = (
        prompt 
        | ollama_model_one_number.with_config(configurable={"output_token_number": 1})
        | StrOutputParser())
    role_number = chain.invoke({"query": query, "role_options": role_options})

    try:
        selected_role = ROLES[role_number.strip()]["name"]
    except KeyError:
        print(f"Invalid role number: {role_number}")
        selected_role = "回答ロールが選択されませんでした。"

    return {"current_role": selected_role}


# answeringノードの実装
# 回答を生成するノード
def answering_node(state: State) -> dict[str, Any]:
    query = state.query
    role = state.current_role
    role_details = "\n".join([f"- {v['name']}: {v['details']}" for v in ROLES.values()])
    prompt = ChatPromptTemplate.from_template(
        """あなたは{role}として回答してください。以下の質問に対して、あなたの役割に基づいた適切な回答を提供してください。

        役割の詳細:
        {role_details}

        質問: {query}

        回答:""".strip()
    )
    chain = prompt | ollama_model | StrOutputParser()
    answer = chain.invoke({"role": role, "role_details": role_details, "query": query})
    return {"messages": [answer]}


# checkノードの実装
class Judgement(BaseModel):
    judge: bool = Field(default=False, description="判定結果")
    reason: str = Field(default="", description="判定理由")
# 回答の品質をチェックするノード
def check_node(state: State) -> dict[str, Any]:
    query = state.query
    answer = state.messages[-1]
    prompt = ChatPromptTemplate.from_template(
"""以下の回答の品質をチェックし、問題がある場合は'False'、問題がない場合は'True'を回答してください。
また、その判断理由も説明してください。

ユーザーからの質問: {query}
回答: {answer}
""".strip()
    )
    chain = prompt | ollama_model.with_structured_output(Judgement)
    result: Judgement = chain.invoke({"query": query, "answer": answer})

    return {
        "current_judge": result.judge,
        "judgement_reason": result.reason
    }



if __name__ == "__main__":

    # 初期ステートを入力として、選択ノードを実行します
    # State.query = "LLMについて教えてください。"

    # result = selection_node(State)
    # print(result["current_role"])


    # State.query = "what is the Japanese word for 'apple'?"

    # result = selection_node(State)
    # print(result["current_role"])

    # Graphの作成
    workflow = StateGraph(State)

    # ノードの追加
    workflow.add_node("selection", selection_node)
    workflow.add_node("answering", answering_node)
    workflow.add_node("check", check_node)

    # エッジの定義
    # selectionノードから開始
    workflow.set_entry_point("selection")
    # selectionノードからansweringノードへ
    workflow.add_edge("selection", "answering")
    # answeringノードからcheckノードへ
    workflow.add_edge("answering", "check")

    # 条件付きのエッジの定義
    # checkノードから次のノードへの遷移に条件付きエッジを定義
    # state.current_jedgeがTrueの場合、ENDノードへ遷移
    # state.current_jedgeがFalseの場合、selectionノードへ遷移
    workflow.add_conditional_edges(
        "check",
        lambda state: state.current_judge,
        {True: END, False: "selection"}
    )

    # グラフのコンパイル
    compiled_graph = workflow.compile()
    
    # グラフの実行
    initial_state = State(query="生成AIについて教えてください。")
    # result = compiled_graph.invoke(initial_state)
    # pp.pprint(result)

    # for chunk, meta in compiled_graph.stream(initial_state, stream_mode="messages"):
    #     print(chunk.content, end="", flush=True)

    for values in compiled_graph.stream(initial_state, stream_mode="debug"):
        pp.pprint(values)


# StreamMode = Literal["values", "updates", "debug", "messages", "custom"]
# """How the stream method should emit outputs.

# - `"values"`: Emit all values in the state after each step.
#     When used with functional API, values are emitted once at the end of the workflow.
# - `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.
#     If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately.
# - `"custom"`: Emit custom data using from inside nodes or tasks using `StreamWriter`.
# - `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.
# - `"debug"`: Emit debug events with as much information as possible for each step.
# """