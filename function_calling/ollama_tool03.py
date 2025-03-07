# https://python.langchain.com/docs/how_to/tool_calling/
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from typing_extensions import Annotated, TypedDict
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.messages.tool import InvalidToolCall
import json

chatModel = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://localhost:11434",
    )

@tool
def add(a: int, b: int) -> int:
    """Adds a and b. returns a + b."""
    print(f"足し算をするよ: {a} + {b}")
    return a + b

# 引き算
@tool
def subtract(a: int, b: int) -> int:
    """Subtracts b from a. returns a - b."""
    print(f"引き算をするよ: {a} - {b}")
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a by b. returns a * b."""
    print(f"掛け算をするよ: {a} * {b}")
    return a * b

@tool
def divide(a: int, b: int) -> float:
    """Divides a by b. returns a / b."""
    print(f"割り算をするよ: {a} / {b}")
    return a / b


tool_list = [add, subtract, multiply, divide]
chatModel_with_tools = chatModel.bind_tools(tool_list)

# query = "What is 3 * 12? Also, what is 11 + 49?"
query = "3 * 12 - 6 + 70 = ?"
query = "3 * 12 + 70- 6  = ?"
# query = "3 * 12 - 6 + 70 = ?"

response = chatModel_with_tools.invoke(query)
response_json = json.loads(response.model_dump_json())
print(response_json)
try:
    if response_json["tool_calls"] is None or len(response_json["tool_calls"]) == 0:
        res = chatModel.invoke(query)
        # print("tool_calls is None.")
        res_json = json.loads(res.model_dump_json())
        print(res_json.get("content"))
        
    else:
        for tool_call in response_json["tool_calls"]:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            # toolsの中に該当する関数を取得
            tools = [tl for tl in tool_list if tl.name == tool_name]
            if len(tools) == 0:
                print(f"Tool {tool_name} not found.")
                continue
            tool_func = tools[0]
            # print(tool_func)
            print(f"{tool_name}({tool_args})を実行します")
            tool_result = tool_func.invoke(tool_args)
            print(tool_result)
except KeyError:
    print("No tool is called.")

# 計算結果を次の計算に使用していないので、上手くいかないようです
# 計算の引数が考察で作られてしまっています
# 評価と計算を繰り返すようにする必要があります
# また、計算結果を保存しておく必要があります
