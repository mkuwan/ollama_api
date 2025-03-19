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
from langchain_core.runnables import RunnableParallel
from operator import itemgetter


model = ChatOpenAI(
    # model="mistral:latest",
    model="llama3.2",
    temperature=0.3,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

# model = ChatOllama(
#     model="llama3.2",
#     temperature=0,
#     base_url="http://localhost:11434",
# )

output_parser = StrOutputParser()

optimistic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "あなたは楽観主義者です。ユーザーの入力に対して楽観的な意見を提供してください。"),
        ("human", "{topic}"),
    ]
)

optimisci_chain = optimistic_prompt | model | output_parser


pessimistic_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "あなたは悲観主義者です。ユーザーの入力に対して悲観的な意見を提供してください。"),
        ("human", "{topic}"),
    ]
)

pessimisci_chain = pessimistic_prompt | model | output_parser


# parallel_chain = RunnableParallel(
#     {
#         "optimistic": optimisci_chain,
#         "pessimistic": pessimisci_chain,
#         "topic": itemgetter("topic"),
#     }
# )

synthesize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "あなたは客観的な視点を持っています。{topic}について2つの意見をまとめたうえで結論を提供してください。"),
        ("human", "楽観的意見:{optimistic}\n 悲観的意見:{pessimistic}"),
    ]
)

synthesize_chain = (
    {
        "optimistic": optimisci_chain,
        "pessimistic": pessimisci_chain,
        "topic": itemgetter("topic"),
    }
    | synthesize_prompt
    | model
    | output_parser
)

# output = synthesize_chain.invoke({"topic": "生成AIの未来はどうなるでしょうか？"})
# print(output)
for chunk in synthesize_chain.stream({"topic": "JavaとC#とPyhonの将来性はどうなるでしょうか？"}):
    print(chunk, end="", flush=True)


