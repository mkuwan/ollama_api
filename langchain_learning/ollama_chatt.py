from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

from langgraph.prebuilt import create_react_agent
from langchain_community.tools.bing_search import BingSearchResults
from langchain_community.utilities import BingSearchAPIWrapper

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
# from langgraph.checkpoint.memory import MemorySaver 


# memory = MemorySaver()
chat = ChatOllama(
    model="mistral:latest",
    temperature=0,
    base_url="http://localhost:11434"
)

messages = [
     SystemMessage("You are a helpful assistant."),
     HumanMessage("こんにちは！私はジョンと言います！"),
     AIMessage(content="こんにちは、ジョンさん！どのようにお手伝いできますか？"),
     HumanMessage(content="私の名前がわかりますか？"),
 ]

for chunk in chat.stream(messages):
    print(chunk.content, end="", flush=True)
