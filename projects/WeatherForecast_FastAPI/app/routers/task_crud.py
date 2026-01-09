# Task Endpoints (CRUD)
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import col, select
from app.models import Task, User
from app.dependency import DBSession, ForecastDep
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskWithWeather, WeatherData


router = APIRouter(prefix='/tasks')

@router.post('/', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: DBSession):
    # verify user exists
    user = db.get(User, task.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # create task instance
    # model_dump() convert a Pydantic (or SQLModel) model into a standard Python dict
    db_task = Task(**task.model_dump())

    db.add(db_task)
    db.commit()
    
    db.refresh(db_task)
    # with refresh, the returned object includes things like the auto-generated id or timestamp fields
    return db_task

@router.get('/', response_model=list[TaskResponse])
def get_tasks(
    db: DBSession,
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    city: Optional[str] = Query(None, description="Filter by city (case-insensitive)")
):
    """List all tasks with optional filtering."""
    statement = select(Task)
    if user_id is not None:
        statement = statement.where(Task.user_id == user_id)
    
    if city is not None:
        # statement = statement.where(Task.city.ilike(city))
        # Cannot access member "ilike" for type "str"
        statement = statement.where(col(Task.city).ilike(city))
        # ILIKE: "SEATTLE", "sEaTtLe" all match to "Seattle"

    tasks = db.exec(statement).all()
    return tasks


@router.get('/{task_id}', response_model=TaskWithWeather)
async def get_task(task_id: int, db: DBSession, forecast_client: ForecastDep):
    """Get a specific task with weather forecast."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Fetch weather data (async)
    weather_data = await forecast_client.get_weather(task.city)

    return TaskWithWeather(
        id = task.id, # type: ignore
        title=task.title,
        content=task.content,
        city=task.city,
        user_id=task.user_id,
        weather=WeatherData(**weather_data)
    )

@router.put('/{task_id}', response_model=TaskUpdate)
def update_task(task_id: int, new_task: TaskUpdate, db: DBSession):
    """Update a task."""
    db_task = db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # if updating user_id, verify the new user exists
    if new_task.user_id is not None:
        user = db.get(User, new_task.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
    # update only provided fields
    update_data = new_task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        # Sets the named attribute on the given object to the specified value.
        # setattr(x, 'y', v) is equivalent to x.y = v''

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DBSession):
    """Delete a task."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    db.delete(task)
    db.commit()
    return None 

