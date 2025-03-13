from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("Weather", port=8002)

@mcp.tool()
def set_openweather_api_key(api_key: str) -> str:
    """Set the API key for the weather service  
    
    Args:
        api_key: The API key to set
    """
    os.environ["OPENWEATHER_API_KEY"] = api_key
    return f"OPENWEATHER_API_KEY environment variable set to {api_key}"

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a city using OpenWeatherMap API
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        A description of the current weather conditions
    """
    # Using a free API that doesn't require authentication
    if "OPENWEATHER_API_KEY" not in os.environ:
        return "OPENWEATHER_API_KEY environment variable is not set, please set it using the set_openweather_api_key tool"
    api_key = os.environ["OPENWEATHER_API_KEY"]
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = httpx.get(url)
    response.raise_for_status()
    
    data = response.json()
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    
    return f"{weather.capitalize()}, {temp}°C, {humidity}% humidity, wind {wind} m/s"


if __name__ == "__main__":
    mcp.run(transport='sse')
