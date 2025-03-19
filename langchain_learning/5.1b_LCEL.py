from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

cot_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "ユーザーの質問にステップバイステップで回答してください"),
        ("human", "{question}"),
    ]
)

# OpenAI 互換でOllamaを使用する場合は, base_url に /v1/ を追加します
model = ChatOpenAI(
    model="mistral:latest",
    temperature=0,
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

output_parser = StrOutputParser()


pre_chain = cot_prompt | model | output_parser


summarize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "ステップバイステップで考えた回答かる結論だけを抽出してください"),
        ("human", "{input}"),
    ]
)

summarize_chain = summarize_prompt | model | output_parser

full_chain = pre_chain | summarize_chain

# response = chain.invoke({"question": "Pythonのインストール方法を教えてください"})
# print(response)

print(f"{"*"}"*10 + "pre_chain" + f"{"*"}"*10)
for chunk in pre_chain.stream({"question": "PythonとC#、Javaのフレームワークの数を教えてください"}):
    print(chunk, end="", flush=True)


print()
print(f"{"*"}"*10 + "summarize_chain" + f"{"*"}"*10)
for chunk in full_chain.stream({"question": "PythonとC#、Javaのフレームワークの数を教えてください"}):
    print(chunk, end="", flush=True)
