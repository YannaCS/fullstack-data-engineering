## Coding Challenge:
# FastAPI Task Management with Weather Forecast

## Challenge Overview

Build a Task Management API using FastAPI that integrates with a weather forecast service. When retrieving a task, the API should automatically include the current weather forecast for the task's city location.

## Requirements

### 1. Data Models

Create two main models using SQLModel or SQLAlchemy:

#### User Model
- `id`: Integer, primary key
- `name`: String, required

#### Task Model
- `id`: Integer, primary key
- `title`: String, required, minimum 3 characters
- `content`: String, required
- `city`: String, required (city name for weather lookup)
- `user_id`: Integer, foreign key to User

### 2. API Endpoints

Implement the following endpoints:

#### User Endpoints (CRD - No Update)
- `POST /users` - Create a new user
- `GET /users` - List all users
- `GET /users/{user_id}` - Get a specific user
- `DELETE /users/{user_id}` - Delete a user

#### Task Endpoints (CRUD)
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks (with filtering support)
- `GET /tasks/{task_id}` - Get a specific task **with weather forecast**
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

### 3. Filtering Requirements

The `GET /tasks` endpoint must support query parameters:
- `user_id`: Filter tasks by user ID
- `city`: Filter tasks by city name (case-insensitive)

Examples:
- `GET /tasks?user_id=1` - Get all tasks for user 1
- `GET /tasks?city=tokyo` - Get all tasks in Tokyo (matches "Tokyo", "TOKYO", "tokyo")
- `GET /tasks?user_id=1&city=london` - Get all tasks for user 1 in London

### 4. Weather Forecast Integration

When retrieving a single task (`GET /tasks/{task_id}`), include current weather data.
The Forecast client request has to be ASYNC.

#### Step 1: Get Coordinates from City Name
Use the **Open-Meteo Geocoding API** to get latitude and longitude:
```
GET https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json
```

**Response example:**
```json
{
  "results": [
    {
      "id": 2643743,
      "name": "London",
      "latitude": 51.50853,
      "longitude": -0.12574,
      "country": "United Kingdom"
    }
  ]
}
```

**Error handling:** If `results` is empty or missing, return a 404 error with message "City not found".

#### Step 2: Get Weather Forecast
Use the **Open-Meteo Weather API** with the coordinates:
```
GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true
```

**Response example:**
```json
{
  "current_weather": {
    "temperature": 15.3,
    "windspeed": 12.5,
    "weathercode": 3,
    "time": "2024-01-15T14:00"
  }
}
```

#### Expected Task Response Format
```json
{
  "id": 1,
  "title": "Visit the office",
  "content": "Quarterly review meeting",
  "city": "London",
  "user_id": 1,
  "weather": {
    "temperature": 15.3,
    "windspeed": 12.5,
    "weathercode": 3,
    "time": "2024-01-15T14:00"
  }
}
```

### 5. Dependency Injection Requirements

Implement **two dependency functions**:

#### Database Dependency
```python
def get_db() -> Generator[Session, None, None]:
    """Provide database session"""
    # Your implementation
    pass
```

#### Forecast Client Dependency
```python
def get_forecast_client() -> ForecastClient:
    """Provide weather forecast client"""
    # Your implementation
    pass
```

Use these dependencies in your route handlers:
```python
@app.get("/tasks/{task_id}")
def get_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
    forecast_client: Annotated[ForecastClient, Depends(get_forecast_client)]
):
    # Your implementation
    pass
```

### 6. Validation Requirements

Implement the following validations using Pydantic:

- **Title**: Minimum 3 characters, required
- **Content**: Required, cannot be empty
- **City**: Required, cannot be empty
- **User name**: Required, cannot be empty

### 7. Error Handling

Implement proper error responses:

- **404 Not Found**: When task/user doesn't exist or city not found
```json
  {
    "detail": "Task not found"
  }
```
```json
  {
    "detail": "City not found"
  }
```

## Example Usage

### Create a user
```bash
POST /users
{
  "name": "Alice"
}
```

### Create a task
```bash
POST /tasks
{
  "title": "Team meeting",
  "content": "Discuss Q4 objectives",
  "city": "Tokyo",
  "user_id": 1
}
```

### Get task with weather
```bash
GET /tasks/1

Response:
{
  "id": 1,
  "title": "Team meeting",
  "content": "Discuss Q4 objectives",
  "city": "Tokyo",
  "user_id": 1,
  "weather": {
    "temperature": 18.5,
    "windspeed": 8.2,
    "weathercode": 1,
    "time": "2024-01-15T10:00"
  }
}
```

### Filter tasks
```bash
GET /tasks?city=tokyo

Response:
[
  {
    "id": 1,
    "title": "Team meeting",
    "content": "Discuss Q4 objectives",
    "city": "Tokyo",
    "user_id": 1
  }
]
```

### City not found error
```bash
GET /tasks/1
(where task 1 has city: "InvalidCityName123")

Response: 404
{
  "detail": "City not found"
}
```

## External API Documentation

- **Geocoding API**: https://open-meteo.com/en/docs/geocoding-api
- **Weather API**: https://open-meteo.com/en/docs

**Note**: These APIs are free and require no API key!