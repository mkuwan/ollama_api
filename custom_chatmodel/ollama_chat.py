# https://python.langchain.com/docs/integrations/chat/ollama/

import sys
import os

# ChatOllamaはBaseChatModelを継承しています
from langchain_ollama import ChatOllama

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_core.tools import tool




# ------ custom_chatmodel ------ #
def invocation_with_custom_chatmodel():
    from ollama_chat_model import CustomOllamaChatModel

    print(f"{"*" * 10} custom_chatmodel {"*" * 10}")
    API_CHAT_URL = "http://localhost:11434/api/chat"
    
    chatModel = CustomOllamaChatModel(
        model="llama3.2",
        end_point=API_CHAT_URL,
        temperature=0,
        # other params...
    )
    messages = [
        SystemMessage("You are a helpful assistant that translates English to Japanese. Translate the user sentence."),
        HumanMessage("I like using C# Programing. It's very fun."),
    ]

    # ai_msg = chatModel.invoke(messages)
    # print(ai_msg.content)

    for chunk in chatModel.stream(messages):
        print(chunk.content, end='', flush=True)



# ------ Invocation ------ #
def invocation():
    print(f"{"*" * 10} Invocation {"*" * 10}")
    chatModel = ChatOllama(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0,
        # other params...
    )
    messages = [
        SystemMessage("You are a helpful assistant that translates English to Japanese. Translate the user sentence."),
        HumanMessage("I like using C# Programing. It's very fun."),
    ]

    # ai_msg = chatModel.invoke(messages)
    # print(ai_msg.content)

    for chunk in chatModel.stream(messages):
        print(chunk.content, end='', flush=True)


# ------ Chaining ------ #
def chaining01():
    print(f"{"*" * 10} Chaining 01 {"*" * 10}")
    chatModel = ChatOllama(
        model="llama3.2",
        temperature=0,
        base_url="http://localhost:11434",
        # other params...
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that translates {input_language} to {output_language}.",
            ),
            ("human", "{input}"),
        ]
    )

    input_params = {
        "input_language": "English",
        "output_language": "Japanese",
        "input": "I less like Java programming.",
    }

    messages = prompt.format_messages(**input_params)
    response = chatModel.invoke(messages)
    print(response.content)


def chaining02():
    print(f"{"*" * 10} Chaining 02 {"*" * 10}")
    chatModel = ChatOllama(
        model="llama3.2",
        temperature=0,
        base_url="http://localhost:11434",
        # other params...
    )
    # このような書き方にすることもできます
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that translates {input_language} to {output_language}.",
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | chatModel
    response =  chain.invoke(
        {
            "input_language": "English",
            "output_language": "Japanese",
            "input": "I love programming by TypeScript.",
        }
    )

    print(response.content)


if __name__ == "__main__":
    invocation_with_custom_chatmodel()
    invocation()
    chaining01()
    chaining02()
