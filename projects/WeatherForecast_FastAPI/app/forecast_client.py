import httpx
from fastapi import HTTPException, Depends
from typing import Annotated

class ForecastClient:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    async def get_coordinates(self, city: str) -> tuple[float, float]:
        """Get latitude and longitude for a city name."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GEOCODING_URL,
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                raise HTTPException(status_code=404, detail="City not found")
            
            result = data["results"][0]
            return result["latitude"], result["longitude"]
        
    async def get_weather(self, city: str) -> dict:
        """Get current weather for a city."""
        lat, lon = await self.get_coordinates(city)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.WEATHER_URL,
                params={
                    "latitude": lat, 
                    "longitude": lon, 
                    "current_weather": "true"
                }
            )
            response.raise_for_status()
            data = response.json()

            current = data["current_weather"]
            return {
                "temperature": current["temperature"],
                "windspeed": current["windspeed"],
                "weathercode": current["weathercode"],
                "time": current["time"]
            }
        
def get_forecast_client() -> ForecastClient:
    return ForecastClient()