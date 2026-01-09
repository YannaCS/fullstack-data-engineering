import requests
from typing import Dict, Optional


class WeatherAPIClient:
    
    def __init__(self, api_key: str = "demo_key"):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str) -> Dict:
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def parse_weather_data(self, raw_data: Dict) -> Dict:
        return {
            "temperature": raw_data["main"]["temp"],
            "description": raw_data["weather"][0]["description"],
            "humidity": raw_data["main"]["humidity"],
            "city": raw_data["name"]
        }
