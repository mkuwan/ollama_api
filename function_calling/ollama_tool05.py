import asyncio
from ollama import AsyncClient, Client
import json
import math
import requests

# .local_pass.jsonファイルからAPIキーを取得する
with open(".local_pass.json") as f:
    OPEN_WEATHER_API_KEY = json.load(f)["OPEN_WEATHER_API_KEY"]

def get_weathcer_from_city(city_name: str = "Tokyo") -> dict:
    """指定された都市の天気をOpenWeatherAPIを使用して取得する

    Args:
        city_name (str, optional): 都市名. Defaults to "Tokyo". 都市名は必ず英語で指定する

    Returns:
        dict: 天気情報
    """
    # 都市名から天気情報を取得する 
    # https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}
    # https://api.openweathermap.org/data/2.5/weather?q={city name},{country code}&appid={API key}
    # https://api.openweathermap.org/data/2.5/weather?q={city name},{state code},{country code}&appid={API key}
    
    print(f"city_name: {city_name}")
    
    current_weather_response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={
        "q": city_name + ",jp",
        "lang": "ja",
        "units": "metric",
        "appid": OPEN_WEATHER_API_KEY
    })
    current_weather = current_weather_response.json()
    print(f"get_weathcer_from_city: {current_weather}")
    return {
        "city_name": current_weather["name"],
        "description": current_weather["weather"][0]["description"],
        "temparature": math.floor(current_weather["main"]["temp"])
    }
    

# Extract relevant content from search results since a lot of data is returned from the API
def extract_content(search_results: dict) -> str:
    content = []

    if "organic_results" in search_results:
        for result in search_results["organic_results"][:4]:  # Taking the top 4 results
            if "snippet" in result:
                content.append(result["snippet"])

    if "answer_box" in search_results and search_results["answer_box"]:
        if "answer" in search_results["answer_box"]:
            content.insert(0, search_results["answer_box"]["answer"])

    return "\n\n".join(content)



def simple_query(query: str) -> str:
    import requests
    # Define our search tool
    search_tool = {
        'type': 'function',
        'function': {
            'name': 'get_weathcer_from_city',
            'description': 'Search the weather of a city',
            'parameters': {
                'type': 'object',
                'required': ['city_name'],
                'properties': {
                    'city_name': {
                        'type': 'string',
                        'description': 'The name of the city to search for the weather'
                    }
                }
            }
        }
    }

    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        'tools': [search_tool]
    }


    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data),
    )

    print(f"{"*" * 10} process_query response {"*" * 10}")
    print(response.json())



async def process_query(query: str) -> str:
    client = AsyncClient()

    # Define our search tool
    search_tool = {
        'type': 'function',
        'function': {
            'name': 'get_weathcer_from_city',
            'description': 'Search the weather of a city',
            'parameters': {
                'type': 'object',
                'required': ['city_name'],
                'properties': {
                    'city_name': {
                        'type': 'string',
                        'description': 'The name of the city to search for the weather'
                    }
                }
            }
        }
    }

    # First, let Ollama decide if it needs to search
    response = await client.chat(
        'llama3.2',
        messages=[{
            'role': 'user',
            'content': f'Answer this question: {query}'
        }],
        tools=[search_tool]
    )


    print(f"{"*" * 10} response {"*" * 10}")
    print(response.model_dump_json())



    # Initialize available functions
    available_functions = {
        'get_weathcer_from_city': get_weathcer_from_city
    }

    # Check if Ollama wants to use the search tool
    if response.message.tool_calls:
        print("Searching the wether...")

        for tool in response.message.tool_calls:
            if function_to_call := available_functions.get(tool.function.name):
                # Call the search function
                search_results = function_to_call(**tool.function.arguments)

                if "error" in search_results:
                    if search_results["error"] == "authentication_failed":
                        return "Authentication failed. Please check your API key."
                    return f"Search error: {search_results['error']}"

                return search_results

                # # Extract relevant content
                # content = extract_content(search_results)

                # if not content:
                #     return "No relevant information found."

                # Add the search results to the conversation
                # messages = [
                #     {'role': 'user', 'content': query},
                #     response.message,
                #     {
                #         'role': 'tool',
                #         'name': tool.function.name,
                #         'content': content
                #     }
                # ]

                # # Get final response from Ollama with the search results
                # final_response = await client.chat(
                #     'llama3.2',
                #     messages=messages
                # )

                # return final_response.message.content

    # If no tool calls, return the direct response
    return response.message.content

async def main():
    question = "How's the weather in city Kamakura? "
    print("\nProcessing your question...")
    answer = await process_query(question)
    print("\nAnswer:")
    print(answer)

if __name__ == "__main__":
    # asyncio.run(main())


    simple_query("How's the weather in city Kamakura? ")