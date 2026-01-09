from fastapi import FastAPI

app = FastAPI(
    title="fast api project"
)

@app.get('/')
def home():
    return {'message': 'hello world'}

@app.get('/items/{item_id}')
def get_item(item_id: int, limit: int | None=None):
    return {
        'the input item id: ': item_id,
        'limit': limit
    }
    