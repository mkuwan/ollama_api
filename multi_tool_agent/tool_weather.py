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

    if city_name is None or city_name == "":
        return "都市名が指定されていません。", 400
    
    try:
        current_weather_response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={
            "q": city_name,
            "lang": "ja",
            "units": "metric",
            "appid": OPEN_WEATHER_API_KEY
        })

        current_weather_response.raise_for_status() 
        current_weather = current_weather_response.json()
        return f"{current_weather['name']}の天気は{current_weather['weather'][0]['description']}、気温は{math.floor(current_weather['main']['temp'])}度です。", current_weather_response.status_code
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            return f"{city_name}の天気情報は見つかりませんでした。都市名を確認してください。", err.response.status_code
        else:
            return f"天気情報の取得に失敗しました: {err}", err.response.status_code
        


if __name__ == "__main__":
    response, code = get_weathcer_from_city("kanagawa")
    print(response, code)
