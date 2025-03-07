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

def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b

tools_01 = [add, multiply]


#-------- pydanitcのモデルを使った例
class add_class(BaseModel):
    """Add two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply_class(BaseModel):
    """Multiply two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")

tools_02 = [add_class, multiply_class]


#-------- TypedDictを使った例
class add_dict(TypedDict):
    """Add two integers."""

    # Annotations must have the type and can optionally include a default value and description (in that order).
    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


class multiply_dict(TypedDict):
    """Multiply two integers."""

    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]

tools_03 = [add_dict, multiply_dict]


chatModel = ChatOllama(
        model="llama3.2",
        temperature=0,
        base_url="http://localhost:11434",
        # other params...
    )

with_tool_01 = chatModel.bind_tools(tools_01)
with_tool_02 = chatModel.bind_tools(tools_02)
with_tool_03 = chatModel.bind_tools(tools_03)


query = "What is 3 * 12? Also, what is 11 + 49?"


print(f"{"*" * 10} tools_01 {"*" * 10}")
response_01 = with_tool_01.invoke(query) # .tool_calls
print(response_01)

print(f"{"*" * 10} tools_02 {"*" * 10}")    
response_02 = with_tool_02.invoke(query).tool_calls
print(response_02)

print(f"{"*" * 10} tools_03 {"*" * 10}")
response_03 = with_tool_03.invoke(query) # .tool_calls
print(response_03)

# 属性.tool_callsには有効なツール呼び出しが含まれている必要があります。
# 場合によっては、モデル プロバイダーが不正なツール呼び出し (有効な JSON ではない引数など) を
# 出力することがあることに注意してください。
# このような場合に解析が失敗すると、InvalidToolCallのインスタンスが属性 に設定されます.
# invalid_tool_calls にはInvalidToolCall、名前、文字列引数、識別子、およびエラー メッセージを含めることができます。