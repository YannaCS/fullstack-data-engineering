from fastapi import FastAPI, Header

app = FastAPI(
    title="fast api project"
)

@app.get('/')
def home():
    return {'message': 'hello world'}

@app.get('/items/{item_id}')
def get_item(
    item_id: int, 
    limit: int | None=None,
    user_agent: str = Header(...)
):
    return {
        'the input item id: ': item_id,
        'limit': limit,
        'user_agent': user_agent
    }
    