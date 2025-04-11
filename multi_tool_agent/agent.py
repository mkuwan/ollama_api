import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from tool_weather import get_weathcer_from_city
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search


# def get_weather(city: str) -> dict:
#     """Retrieves the current weather report for a specified city.

#     Args:
#         city (str): The name of the city for which to retrieve the weather report.

#     Returns:
#         dict: status and result or error msg.
#     """
#     try:
#         weather_report, code = get_weathcer_from_city(city)
#         if code != 200:
#             return {
#                 "status": "error",
#                 "error_message": weather_report
#             }
        
#         return {
#             "status": "success",
#             "report": (weather_report)
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "error_message": str(e)
#         }
    
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    # LiteLLM knows how to connect to a local Ollama server by default
    model=LiteLlm(model="ollama/llama3.2"), # Standard LiteLLM format for Ollama
    # model="gemini-2.0-flash-exp",
    name="ollama_agent",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "I can answer your questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time ] #, google_search],
)


# if __name__ == "__main__":
#     # Run the agent with a test query
#     response = get_weather("Tokyo")
#     print(response)  # Expected to print the weather report for Tokyo

#     root_agent.run_async