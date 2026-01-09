from fastapi import FastAPI, Header, Query, Path, Body
from app.routers.task_crud import router as task_router
from app.routers.user_crd import router as user_router

app = FastAPI(
    title = "FastAPI Task Management with Weather Forecast"
)

app.include_router(user_router)
app.include_router(task_router)

@app.get('/')
def home():
    return {"message": "Welcome to the Weather Forecast Task Management Dashboard"}