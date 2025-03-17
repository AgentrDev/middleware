from agentr.server import ApiMCP
from agentr.store.env import EnvStore
import httpx

class WeatherMCP(ApiMCP):
    def __init__(self):
        super().__init__("Weather", instructions=None, port=8002)
        # Add tools
        self.add_tool(self.get_weather)
        self.add_tool(self.authorize)
        self.credential_store = EnvStore()
        
    def validate(self):
        if not self.credential_store.retrieve_credential("OPENWEATHER_API_KEY"):
            raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
    
    def authorize(self, api_key: str):
        """Set the API key for the weather service  
        Args:
            api_key: The API key to set
        """
        self.credential_store.save_credential("OPENWEATHER_API_KEY", api_key)
        return f"OPENWEATHER_API_KEY environment variable set to {api_key}"
    
    
    def _get(self, url, params):
        headers = self.get_headers()
        params = {
            "appid": self.api_key,
            **params
        }
        response = httpx.get(url, headers=headers, params=params)
        return response.json()

    def get_weather(self, city: str):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "units": "metric"
        }
        data = self._get(url, params)
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        return f"{weather.capitalize()}, {temp}°C, {humidity}% humidity, wind {wind} m/s"

    @property
    def api_key(self):
        return self.credential_store.retrieve_credential("OPENWEATHER_API_KEY")

mcp = WeatherMCP()


if __name__ == "__main__":
    mcp.run(transport='sse')
