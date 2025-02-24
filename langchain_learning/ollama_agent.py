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
from langgraph.checkpoint.memory import MemorySaver 


# Create the Ollama Agent
memory = MemorySaver()
model = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://localhost:11434"
)

api_wrapper = BingSearchAPIWrapper(bing_subscription_key="your_key_here")
search = BingSearchResults(num_results=2)

# Bing F1 (3 Calls per second, 1000 calls per month)
