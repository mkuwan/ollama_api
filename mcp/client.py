from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

server_params = StdioServerParameters(
    command="python",
    args=["N:\\python_projects\\ollama_api\\mcp\\math_server.py"]

)

model = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://localhost:11434",
)


# async def run_client() -> None:
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()

#             tools = await load_mcp_tools(session)

#             agent = create_react_agent(model, tools)
#             agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})

#             print()
#             print("response:")
#             print(agent_response)
#             print()

#             print("messages:")
#             for message in agent_response["messages"]:
#                 print(f"  {message}")


async def run_client() -> None:
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["N:\\python_projects\\ollama_api\\mcp\\math_server.py"],
                "transport": "stdio",
            },
            # "weather": {
            #     # make sure you start your weather server on port 8000
            #     "url": "http://localhost:8000/sse",
            #     "transport": "sse",
            # }
            "weather": {
                "command": "python",
                "args": ["N:\\python_projects\\ollama_api\\mcp\\weather_server.py"],
                "transport": "stdio",
            }
        }
    ) as client:
        
        sys_message = SystemMessage(
            content="あなたは天気を調べたり、計算をしたりすることができるAIアシスタントです。"
        )
        agent = create_react_agent(model, client.get_tools(), prompt=sys_message)

        math_response = await agent.ainvoke({"messages": "(4 + 11) x 2 を計算してください"})

        print("math_response:")
        for message in math_response["messages"]:
            print(f"{message}")


        weather_response = await agent.ainvoke({"messages": "kawasakiの天気は？"})

        print("weather_response:")
        for message in weather_response["messages"]:
            print(f"{message}")





if __name__ == "__main__":
    import asyncio
    asyncio.run(run_client())