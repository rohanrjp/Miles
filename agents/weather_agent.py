from typing import Optional
import httpx
from pydantic_ai import Agent, RunContext
from config.llm_config import gemini_model
from models.domain import User


# --- Define the Weather Assistant Agent ---
weather_assistant = Agent(
    model=gemini_model,
    system_prompt="""
        You are the WeatherAssistant. Your primary job is to provide accurate weather forecasts by using the `get_weather` tool.

        Your workflow is as follows:
        1. You MUST call the `get_weather` tool in response to the user's query.
        2. Analyze the output you receive from the tool.

        - **Scenario A: The tool returns weather data.** If the tool provides a forecast, your job is to present this information to the user in a clear, friendly sentence.

        - **Scenario B: The tool returns a 'city not found' signal.** If the tool's output contains the phrase "SIGNAL: City not found", it means you lack the necessary information. In this case, your ONLY task is to ask the user for the city they are interested in. Your response must be a direct question.

        **Example Interactions:**
        - User: "What's the weather in Berlin?" -> Tool provides weather -> You say: "The current weather in Berlin is 15°C."
        - User: "How's the weather?" (and no home city) -> Tool returns "SIGNAL: City not found" -> You say: "Of course, which city would you like the weather forecast for?"
    """
)


@weather_assistant.tool
async def get_weather(ctx: RunContext[User], city: Optional[str] = None) -> str:
    """
    Asynchronously retrieves the current weather. It uses an explicitly provided
    city or falls back to the user's home city from the run context. If no
    city can be determined, it returns a specific signal to the agent.

    Args:
        city: The name of the city, if specified by the user in their prompt.
    """
    current_user = ctx.deps
    target_city = city or current_user.home_city

    print(f"TOOL (get_weather): Trying to find weather for city: '{target_city}'")

    if not target_city:
        return "SIGNAL: City not found. Please ask the user for a city."

    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={target_city}&count=1"

    async with httpx.AsyncClient() as client:
        try:
            geo_response = await client.get(geocoding_url)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return f"I couldn't find location data for '{target_city}' in the weather database."

            location = geo_data["results"][0]
            latitude, longitude, timezone = location["latitude"], location["longitude"], location["timezone"]

            # --- THIS IS THE CORRECTED AND VERIFIED LINE ---
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}¤t_weather=true&timezone={timezone}"
            
            print(f"TOOL (get_weather): Calling final weather URL: {weather_url}")

            weather_response = await client.get(weather_url)
            weather_response.raise_for_status()
            
            weather_data = weather_response.json()["current_weather"]

            return f"The current weather in {location['name']} is {weather_data['temperature']}°C with a wind speed of {weather_data['windspeed']} km/h."

        except httpx.HTTPStatusError as e:
            return f"An HTTP error occurred while contacting the weather service: {e.response.status_code}"
        except Exception as e:
            return f"An unexpected error occurred in the weather tool: {e}"
