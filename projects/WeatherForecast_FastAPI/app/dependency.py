from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from typing import Annotated
from app.forecast_client import ForecastClient, get_forecast_client

DBSession = Annotated[Session, Depends(get_session)]

ForecastDep = Annotated[ForecastClient, Depends(get_forecast_client)]