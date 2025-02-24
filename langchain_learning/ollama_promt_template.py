# https://python.langchain.com/docs/concepts/prompt_templates/

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from typing import List
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def use_prompt_template():
    prompt_template = PromptTemplate.from_template("Tell me joke about {topic}")

    prompt = prompt_template.invoke({"topic": "chickens"})
    
    # returns "Tell me joke about chickens"
    print(prompt)


def use_chat_prompt_template():
    chat_prompt_template = ChatPromptTemplate([
        ("system", "You are a helpful assistant"),
        ("user", "Tell me a joke about {topic}")
    ])

    chat_prompt = chat_prompt_template.invoke({"topic": "chickens"})
    
    # returns 
    # messages=[
    # SystemMessage(content='You are a helpful assistant', additional_kwargs={}, response_metadata={}), 
    # HumanMessage(content='Tell me a joke about chickens', additional_kwargs={}, response_metadata={})]
    print(chat_prompt)

def use_messages_placeholder():
    prompt_template = ChatPromptTemplate([
        ("system", "You are a helpful assistant"),
        MessagesPlaceholder("msgs")
    ])

    # messages=[
    # SystemMessage(content='You are a helpful assistant', additional_kwargs={}, response_metadata={}), 
    # HumanMessage(content='hi!', additional_kwargs={}, response_metadata={})]
    messages = prompt_template.invoke({"msgs": [HumanMessage(content="hi!")]})

    print(messages)



if __name__ == "__main__":
    print(f"{"*" * 10} prompt_template {"*" * 10}")
    use_prompt_template()

    print(f"{"*" * 10} chat_prompt_template {"*" * 10}")
    use_chat_prompt_template()

    print(f"{"*" * 10} messages_placeholder {"*" * 10}")
    use_messages_placeholder()
