from sqlalchemy.orm import Session
from app.models import WeatherLog
from app.external_api import WeatherAPIClient
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import func

class WeatherService:
    
    def __init__(self, db: Session, api_client: WeatherAPIClient):
        self.db = db
        self.api_client = api_client
    
    def get_weather(self, city: str) -> Dict:
        raw_data = self.api_client.get_current_weather(city)
        weather_data = self.api_client.parse_weather_data(raw_data)
        
        log = WeatherLog(
            city=weather_data["city"],
            temperature=weather_data["temperature"],
            description=weather_data["description"]
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return weather_data
    
    def get_history(self, city: str, days: int = 7) -> List[WeatherLog]:
        since = datetime.now() - timedelta(days=days)
        return self.db.query(WeatherLog).filter(
            func.lower(WeatherLog.city) == city.lower(),
            WeatherLog.queried_at >= since
        ).all()
    
    def calculate_average_temp(self, city: str, days: int = 7) -> float:
        history = self.get_history(city, days)
        
        if not history:
            raise ValueError(f"No weather data found for {city}")
        
        total = sum(log.temperature for log in history)
        return round(total / len(history), 2)
