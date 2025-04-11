from typing import List
from mcp.server.fastmcp import FastMCP
import json
import math
import requests


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
    # print(f"get_weathcer_from_city: {current_weather}")
    # return {
    #     "city_name": current_weather["name"],
    #     "description": current_weather["weather"][0]["description"],
    #     "temparature": math.floor(current_weather["main"]["temp"])
    # }
    return f"{current_weather['name']}の天気は{current_weather['weather'][0]['description']}、気温は{math.floor(current_weather['main']['temp'])}度です。"

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return get_weathcer_from_city(location)

if __name__ == "__main__":
    # mcp.run(transport="sse")
    mcp.run(transport="stdio")