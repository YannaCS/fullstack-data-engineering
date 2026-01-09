## Installing dependency

To install fastapi sqlmodel, run in project directory with venv activated:

```bash
uv pip install "fastapi[standard]" sqlmodel
```

sqlmodel = sqlalchemy + Pydantic   

The `sqlmodel` package combines SQLAlchemy (for database operations) with Pydantic (for data validation).  

fastapi is based on `uvicorn`

## start fastapi server

```bash
fastapi dev main.py
```
This starts a development server with hot-reload enabled, so code changes are automatically reflected.  