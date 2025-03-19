from agentr.application import Application
from agentr.integration import Integration
from agentr.store import Store
import httpx
class OpenWeatherApp(Application):
    def __init__(self, user_id, integration: Integration, store: Store) -> None:
        super().__init__(name="openweather", user_id=user_id, integration=integration, store=store)

    def _get(self, url, params):
        credentials = self.store.retrieve_credential(self.integration.integration_id, self.connection_id)
        params = {
            "appid": credentials['api_key'],
            **params
        }
        response = httpx.get(url, headers=self._get_headers(), params=params)
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
    
    def list_tools(self):
        return [self.get_weather]