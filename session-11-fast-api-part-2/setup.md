## Installing required packages

To install the required packages run in project directory with venv activated:

```bash
uv pip install pyjwt "pwdlib[argon2]" 'pydantic[email]'
```

Install SqlAlchemy async support
```bash
uv pip install asyncpg 'sqlalchemy[asyncio]'
```

Install httpx for async http client

```bash
uv pip install httpx python-dotenv
```
httpx: support async i/o, others like requests doesn't support async i/o    
Python-dotenv: reads key-value pairs from a .env file and can set them as environment variables.

## start fastapi server

```bash
fastapi dev main.py
```