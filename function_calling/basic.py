from langchain_ollama import ChatOllama
import requests
import math
import json

chatModel = ChatOllama(
    model="llama3.2",
    temperature=0,
    base_url="http://localhost:11434",
    # other params...
)

# .local_pass.jsonファイルからAPIキーを取得する
with open(".local_pass.json") as f:
    OPEN_WEATHER_API_KEY = json.load(f)["OPEN_WEATHER_API_KEY"]
    


# OpenWeather で指定の都市の天気を取得する
def get_current_weather(city_name: str = "Tokyo") -> dict:
    """指定された都市の天気をOpenWeatherAPIを使用して取得する

    Args:
        city_name (str, optional): 都市名. Defaults to "Tokyo". 都市名は必ず英語で指定する

    Returns:
        dict: 天気情報
    """

    # 都市の緯度、経度を取得する 
    # https://openweathermap.org/api/geocoding-api
    geocoding_response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params={
        "q": city_name + ",jp",
        "limit": 1,
        "appid": OPEN_WEATHER_API_KEY
    })
    geocodings = geocoding_response.json()
    geocoding = geocodings[0]
    # print(geocoding)
    lat, lon = geocoding["lat"], geocoding["lon"]
 
    # 指定した緯度、経度の現在の天気を取得する
    # https://openweathermap.org/current
    current_weather_response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "lang": "ja",
        "appid": OPEN_WEATHER_API_KEY
    })
    current_weather = current_weather_response.json()
    # print(current_weather)
 
    return {
        "city_name": city_name,
        "description": current_weather["weather"][0]["description"],
        "temparature": math.floor(current_weather["main"]["temp"])
    }


def call_with_function_or_not(query):
    tools = [get_current_weather]
    with_tool = chatModel.bind_tools(tools)
    response = with_tool.invoke(query)

    # responseをjsonフォーマットにする
    response_json = json.loads(response.model_dump_json())
    # print(response_json)
    if "tool_calls" in response_json:
        for tool_call in response_json["tool_calls"]:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            # toolsの中に該当する関数を取得
            tools = [tool for tool in tools if tool.__name__ == tool_name]
            if len(tools) == 0:
                print(f"Tool {tool_name} not found.")
                continue
            tool_func = tools[0]
            print(f"{tool_name}({tool_args})を実行します")
            tool_result = tool_func(**tool_args)
            print(tool_result)
    else:
        print("No tool calls.") 
        print(response_json)



if __name__ == "__main__":
    # 都市の天気を質問してtoolが使用されることを確認します
    query = "What is the weather in Kawasaki?"
    call_with_function_or_not(query)
    
    # 天気とは関係のない質問をしたらToolが選択されないことを確認します
    query = "こんにちは"
    call_with_function_or_not(query)