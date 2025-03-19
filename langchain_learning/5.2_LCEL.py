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


# OpenAI 互換でOllamaを使用する場合は, base_url に /v1/ を追加します
model = ChatOpenAI(
    model="mistral:latest",
    temperature=0,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

prompt = ChatPromptTemplate.from_messages(
     [
         ("system", "You are a helpful assistant."),
         ("human", "{input}"),
     ]
 )

output_parser = StrOutputParser()

def upper(text: str) -> str:
    return text.upper()

chain_sample = prompt | model | output_parser | RunnableLambda(upper)

output = chain_sample.invoke({"input": "Hello!"})
print(output)





# model = ChatOllama(
#     model="llama3.2",
#     temperature=0,
#     base_url="http://localhost:11434",
# )

# @chainはRunnableLambda(lower)と同じになります
@chain
def lower(input_stream: Iterator[str]) -> Iterator[str]:
    for text in input_stream:
        # time.sleep(0.01)
        yield text.lower()

chain_sample = prompt | model | output_parser | lower

# output = chain_sample.invoke({"input": "Hello!"})
# print(output)
for chunk in chain_sample.stream({"input": "Hi there!"}):
    print(chunk, end="", flush=True)