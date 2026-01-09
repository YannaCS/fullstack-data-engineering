from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Base
from app.services import WeatherService
from app.external_api import WeatherAPIClient
from dotenv import load_dotenv
import os
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weather API")


def get_weather_service(db: Session = Depends(get_db)) -> WeatherService:
    api_client = WeatherAPIClient(api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    return WeatherService(db, api_client)


@app.get("/")
def root():
    return {"message": "Weather API 3.0"}


@app.get("/weather/{city}")
def get_weather(city: str, service: WeatherService = Depends(get_weather_service)):
    try:
        weather = service.get_weather(city)
        return weather
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/{city}/history")
def get_weather_history(
    city: str, 
    days: int = 7,
    service: WeatherService = Depends(get_weather_service)
):
    history = service.get_history(city, days)
    return {
        "city": city,
        "days": days,
        "records": [
            {
                "temperature": log.temperature,
                "description": log.description,
                "queried_at": log.queried_at.isoformat()
            }
            for log in history
        ]
    }


@app.get("/weather/{city}/average")
def get_average_temperature(
    city: str,
    days: int = 7,
    service: WeatherService = Depends(get_weather_service)
):
    try:
        avg_temp = service.calculate_average_temp(city, days)
        return {
            "city": city,
            "days": days,
            "average_temperature": avg_temp
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
