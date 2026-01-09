from fastapi import FastAPI

app = FastAPI(
    title="fast api project"
)

@app.get('/')
def home():
    return {'message': 'hello world'}