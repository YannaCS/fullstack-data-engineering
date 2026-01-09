from fastapi import FastAPI, Header, Query, Path
from typing import Optional
app = FastAPI(
    title="fast api project"
)

@app.get('/')
def home():
    return {'message': 'hello world'}

@app.get('/items/{item_id}')
def get_item(
    # with validation: 
    item_id: int = Path(..., description='Item id in path'), 
    # can use Optional as well
    limit: Optional[int] =Query(None, lt=100, description='max items to return'),
    user_agent: str = Header(...)
):
    '''
    This api is to fetch item by id
    '''
    return {
        'the input item id: ': item_id,
        'limit': limit,
        'user_agent': user_agent
    }
    