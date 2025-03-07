# https://python.langchain.com/docs/how_to/tool_calling/
from langchain_ollama import ChatOllama, OllamaLLM
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
import asyncio
from langchain.agents import AgentExecutor, create_tool_calling_agent


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


# プロンプトの定義
prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            '与えられたinputを計算してください。toolを使用してください。' \
            '計算を行う前に、計算の手順(四則演算のルール)を確認してから実行してください。' \
            '回答は日本語でお願いします。', # 計算が正しく行われているか確認しながら丁寧に計算してください。
        ),
        ('human', '{input}'),
        # Placeholders fill up a **list** of messages
        ('placeholder', '{agent_scratchpad}'),
    ]
)

tools=[add, subtract, multiply, divide]

# create agent
agent = create_tool_calling_agent(
    chatModel,
    tools=tools,
    prompt=prompt,
    # output_parser=PydanticToolsParser,
)


# execute agent
query = "3 * 12 - 6 + 70 = ?"
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": query})
print(result)

# 実行結果 間違ってる・・・💦
# ollama_tool03のほうが正しく計算できる
# > Entering new AgentExecutor chain...
# Invoking: `multiply` with `{'a': 3, 'b': 12}`

# 掛け算をするよ: 3 * 12
# 36
# Invoking: `subtract` with `{'a': 108, 'b': 6}`

# 引き算をするよ: 108 - 6
# 102
# Invoking: `add` with `{'a': 102, 'b': 70}`

# 足し算をするよ: 102 + 70
# 172最終的な答えは172です。

# > Finished chain.
# {'input': '3 * 12 - 6 + 70 = ?', 'output': '最終的な答えは172です。'}