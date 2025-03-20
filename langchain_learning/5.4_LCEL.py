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
import os
from langchain_community.retrievers import TavilySearchAPIRetriever


# RunnableParalellを使用する際、その要素の一部で入力の値をそのまま出力したい場合があります。
# 入力をそのまま出力するために使えるのがRunnablePassthroughです。

with open(".local_pass.json") as f:
    TAVILY_API_KEY = json.load(f)["TAVILY_API_KEY"]
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

model = ChatOpenAI(
    model="mistral:latest",
    # model="llama3.2",
    temperature=0.3,
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)

prompt = ChatPromptTemplate.from_template('''\
    以下の文脈だけを踏まえて質問に回答してください。'
    
    文脈:"""'
    {context}
    """

    質問:"""'
    {question}
    """
    ''')

retriever = TavilySearchAPIRetriever(k=3)
# from langchain_community.retrievers import TavilySearchAPIRetriever

retriever = TavilySearchAPIRetriever(k=3)

# chain = (
#     {
#         "context": retriever,
#         "question": RunnablePassthrough(),  # 入力をそのまま出力する
#     }
#     | prompt
#     | model
#     | StrOutputParser()
# )


# chain = (
#     {
#         "context": retriever,
#         "question": RunnablePassthrough(),  # 入力をそのまま出力する
#     }
#     | RunnablePassthrough.assign(           # context と question に answer を追加
#         answer=prompt 
#         | model 
#         | StrOutputParser()
#         )
# )

chain = (RunnableParallel(
    {
        "context": retriever,
        "question": RunnablePassthrough(),  # 入力をそのまま出力する
    }
)
.assign(answer=prompt | model | StrOutputParser())
.pick(["question", "answer"])                # question と answer のみを出力      
)

output = chain.invoke("川崎市の今日の天気は？")
print(output)


# assignを使うことで、contextのようなChainの中間の値をChainの最終出力に含めることができます。
# そのため、プロンプトを穴埋めした結果を画面に表示したい場合など、
# Chainの中間の値をUI上に表示したい場合にもassignが役立ちます。



